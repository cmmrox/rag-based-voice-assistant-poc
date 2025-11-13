'use client';

import { useState, useRef, useCallback } from 'react';
import { WebSocketClient, WebSocketMessage } from '@/lib/websocket';

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
  const websocketRef = useRef<WebSocketClient | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  const startSession = useCallback(async () => {
    try {
      setStatus('connecting');
      setError(null);

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      localStreamRef.current = stream;

      // Create peer connection
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      });

      // Add audio tracks
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
      });

      // Handle incoming audio
      pc.ontrack = (event) => {
        console.log('Received remote track:', event.track.kind);
        if (event.track.kind === 'audio') {
          if (!audioElementRef.current) {
            audioElementRef.current = new Audio();
          }
          audioElementRef.current.srcObject = event.streams[0];
          audioElementRef.current.play().catch(console.error);
        }
      };

      // Handle ICE candidates
      pc.onicecandidate = (event) => {
        if (event.candidate && websocketRef.current?.isConnected()) {
          websocketRef.current.send({
            type: 'ice_candidate',
            candidate: event.candidate,
            session_id: sessionId || ''
          });
        }
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

      peerConnectionRef.current = pc;

      // Connect WebSocket
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002';
      const ws = new WebSocketClient(wsUrl.startsWith('ws://') || wsUrl.startsWith('wss://') 
        ? `${wsUrl}/ws/signaling` 
        : `ws://${wsUrl}/ws/signaling`);
      websocketRef.current = ws;

      await ws.connect();

      // Handle WebSocket messages
      ws.onMessage((message: WebSocketMessage) => {
        handleWebSocketMessage(message, pc);
        
        // Handle transcription and response messages
        if (message.type === 'transcription') {
          const msg = message as any;
          addTranscriptMessage('user', msg.text);
          setStatus('processing');
        } else if (message.type === 'response_text') {
          const msg = message as any;
          addTranscriptMessage('assistant', msg.text);
          setStatus('speaking');
        }
      });

      ws.onError((error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setStatus('error');
      });

      ws.onClose(() => {
        console.log('WebSocket closed');
        setStatus('idle');
      });

      // Request session
      ws.send({
        type: 'session_request'
      });

    } catch (err) {
      console.error('Error starting session:', err);
      setError(err instanceof Error ? err.message : 'Failed to start session');
      setStatus('error');
    }
  }, [sessionId]);

  const handleWebSocketMessage = async (
    message: WebSocketMessage,
    pc: RTCPeerConnection
  ) => {
    if (message.type === 'offer') {
      try {
        await pc.setRemoteDescription(new RTCSessionDescription({
          type: 'offer',
          sdp: message.sdp
        }));

        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        websocketRef.current?.send({
          type: 'answer',
          sdp: answer.sdp,
          type: answer.type,
          session_id: message.session_id
        });

        setSessionId(message.session_id);
      } catch (error) {
        console.error('Error handling offer:', error);
        setError('Failed to handle offer');
        setStatus('error');
      }
    } else if (message.type === 'ice_candidate') {
      try {
        await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
      } catch (error) {
        console.error('Error adding ICE candidate:', error);
      }
    } else if (message.type === 'session_ready') {
      setStatus('connected');
      setSessionId(message.session_id);
    } else if (message.type === 'session_ended') {
      setStatus('idle');
      stopSession();
    }
  };

  const stopSession = useCallback(() => {
    // Stop local stream
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }

    // Close peer connection
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    // Close WebSocket
    if (websocketRef.current) {
      if (sessionId) {
        websocketRef.current.send({
          type: 'end_session',
          session_id: sessionId
        });
      }
      websocketRef.current.close();
      websocketRef.current = null;
    }

    // Stop audio playback
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current = null;
    }

    setStatus('idle');
    setSessionId(null);
  }, [sessionId]);

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
    addTranscriptMessage
  };
}

