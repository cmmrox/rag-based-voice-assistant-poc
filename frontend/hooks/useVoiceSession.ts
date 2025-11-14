'use client';

import { useState, useRef, useCallback } from 'react';

export type SessionStatus = 'idle' | 'connecting' | 'connected' | 'listening' | 'processing' | 'speaking' | 'error';

export interface TranscriptMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export function useVoiceSession() {
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  const startSession = useCallback(async () => {
    try {
      setStatus('connecting');
      setError(null);

      // Get user media (microphone)
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      localStreamRef.current = stream;

      // Create peer connection (no STUN servers needed for OpenAI)
      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;

      // Set up to play remote audio from OpenAI
      audioElementRef.current = document.createElement("audio");
      audioElementRef.current.autoplay = true;
      pc.ontrack = (event) => {
        console.log('Received remote track:', event.track.kind);
        if (event.track.kind === 'audio' && audioElementRef.current) {
          audioElementRef.current.srcObject = event.streams[0];
          audioElementRef.current.play().catch(console.error);
        }
      };

      // Add local audio track for microphone input
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
      });

      // Set up data channel for sending and receiving events
      const dc = pc.createDataChannel("oai-events");
      dataChannelRef.current = dc;

      // Listen for server events from OpenAI
      dc.onmessage = (event) => {
        try {
          const eventData = JSON.parse(event.data);
          console.log('Received event from OpenAI:', eventData);
          
          // Handle different event types
          if (eventData.type === 'conversation.item.input_audio_transcription.completed') {
            const transcript = eventData.transcript || '';
            addTranscriptMessage('user', transcript);
            setStatus('processing');
          } else if (eventData.type === 'response.audio_transcript.delta') {
            const delta = eventData.delta || '';
            if (delta) {
              addTranscriptMessage('assistant', delta);
              setStatus('speaking');
            }
          } else if (eventData.type === 'response.done') {
            setStatus('connected');
          } else if (eventData.type === 'error') {
            setError(eventData.error?.message || 'Unknown error');
            setStatus('error');
          }
        } catch (err) {
          console.error('Error parsing event:', err);
        }
      };

      dc.onopen = () => {
        console.log('Data channel opened');
        setStatus('connected');
      };

      dc.onerror = (err) => {
        console.error('Data channel error:', err);
        setError('Data channel error');
        setStatus('error');
      };

      // Handle connection state changes
      pc.onconnectionstatechange = () => {
        console.log('Connection state:', pc.connectionState);
        if (pc.connectionState === 'connected') {
          setStatus('connected');
        } else if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
          setStatus('error');
          setError('Connection failed');
        }
      };

      // Create offer and send to backend
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // POST SDP to backend endpoint which forwards to OpenAI
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const sdpResponse = await fetch(`${backendUrl}/api/realtime/session`, {
        method: 'POST',
        body: offer.sdp,
        headers: {
          'Content-Type': 'application/sdp',
        },
      });

      if (!sdpResponse.ok) {
        const errorData = await sdpResponse.json().catch(() => ({ error: 'Failed to create session' }));
        throw new Error(errorData.error || 'Failed to create realtime session');
      }

      // Get OpenAI's SDP answer
      const answerSdp = await sdpResponse.text();
      
      // Set remote description with OpenAI's answer
      const answer = {
        type: 'answer' as RTCSdpType,
        sdp: answerSdp,
      };
      
      await pc.setRemoteDescription(new RTCSessionDescription(answer));

      // Generate a session ID for tracking
      setSessionId(crypto.randomUUID());

    } catch (err) {
      console.error('Error starting session:', err);
      setError(err instanceof Error ? err.message : 'Failed to start session');
      setStatus('error');
      stopSession();
    }
  }, []);

  const stopSession = useCallback(() => {
    // Stop local stream
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }

    // Close data channel
    if (dataChannelRef.current) {
      dataChannelRef.current.close();
      dataChannelRef.current = null;
    }

    // Close peer connection
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    // Stop audio playback
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current.srcObject = null;
      audioElementRef.current = null;
    }

    setStatus('idle');
    setSessionId(null);
    setError(null);
  }, []);

  const sendEvent = useCallback((event: object) => {
    if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
      dataChannelRef.current.send(JSON.stringify(event));
    } else {
      console.warn('Data channel not open, cannot send event');
    }
  }, []);

  const addTranscriptMessage = useCallback((role: 'user' | 'assistant', text: string) => {
    setTranscript(prev => [...prev, {
      role,
      text,
      timestamp: new Date().toISOString()
    }]);
  }, []);

  return {
    status,
    transcript,
    error,
    sessionId,
    startSession,
    stopSession,
    sendEvent,
    addTranscriptMessage
  };
}
