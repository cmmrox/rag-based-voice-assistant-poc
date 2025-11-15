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
  const websocketRef = useRef<WebSocket | null>(null);

  const addTranscriptMessage = useCallback((role: 'user' | 'assistant', text: string) => {
    setTranscript(prev => [...prev, {
      role,
      text,
      timestamp: new Date().toISOString()
    }]);
  }, []);

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
      
      // Store session config to be sent when data channel opens
      let sessionConfigToSend: any = null;

      // Listen for server events from OpenAI
      dc.onmessage = async (event) => {
        try {
          const eventData = JSON.parse(event.data);
          console.log('Received event from OpenAI:', eventData);
          
          // Handle different event types
          if (eventData.type === 'conversation.item.input_audio_transcription.completed') {
            const transcript = eventData.transcript || '';
            addTranscriptMessage('user', transcript);
            setStatus('processing');
            // Note: With function calling, RAG queries are handled via function calls
            // No need to manually trigger RAG query here
          } 
          // Handle function call events
          else if (eventData.type === 'conversation.item.completed') {
            const item = eventData.item;
            if (item && item.type === 'function_call') {
              console.log('Function call completed:', item);
              setStatus('processing');
              
              // Parse function arguments (they might come as a string)
              let functionArgs = {};
              try {
                if (typeof item.arguments === 'string') {
                  functionArgs = JSON.parse(item.arguments);
                } else if (item.arguments) {
                  functionArgs = item.arguments;
                }
              } catch (e) {
                console.error('Error parsing function arguments:', e);
                functionArgs = {};
              }
              
              // Send function call to backend for execution
              if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
                websocketRef.current.send(JSON.stringify({
                  type: 'function_call',
                  call_id: item.id || item.call_id,
                  function_name: item.name,
                  arguments: functionArgs
                }));
              }
            }
          }
          // Handle function call updates (arguments being populated)
          else if (eventData.type === 'conversation.updated') {
            const item = eventData.item;
            const delta = eventData.delta;
            
            if (item && item.type === 'function_call') {
              console.log('Function call update:', item, delta);
              // Function call arguments are being populated
              // We'll wait for conversation.item.completed to execute
            }
          }
          else if (eventData.type === 'response.audio_transcript.delta') {
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
        
        // Send session configuration to OpenAI via data channel
        if (sessionConfigToSend) {
          try {
            // Send session.update event with the configuration
            // OpenAI Realtime API expects the session config directly in the event
            const sessionUpdateEvent = {
              type: 'session.update',
              ...sessionConfigToSend
            };
            dc.send(JSON.stringify(sessionUpdateEvent));
            console.log('Sent session configuration to OpenAI');
          } catch (e) {
            console.error('Failed to send session configuration:', e);
          }
        }
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
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8002';
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
      
      // Get session config from response header and store it for data channel
      const sessionConfigHeader = sdpResponse.headers.get('X-Session-Config');
      if (sessionConfigHeader) {
        try {
          sessionConfigToSend = JSON.parse(sessionConfigHeader);
          // If data channel is already open, send config immediately
          if (dc.readyState === 'open') {
            const sessionUpdateEvent = {
              type: 'session.update',
              ...sessionConfigToSend
            };
            dc.send(JSON.stringify(sessionUpdateEvent));
            console.log('Sent session configuration to OpenAI (channel already open)');
          }
        } catch (e) {
          console.error('Failed to parse session config from header:', e);
        }
      }
      
      // Set remote description with OpenAI's answer
      const answer = {
        type: 'answer' as RTCSdpType,
        sdp: answerSdp,
      };
      
      await pc.setRemoteDescription(new RTCSessionDescription(answer));

      // Generate a session ID for tracking
      const newSessionId = crypto.randomUUID();
      setSessionId(newSessionId);

      // Connect to backend WebSocket for RAG integration
      const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
      const wsUrl = backendUrl.replace(/^https?/, wsProtocol);
      const ws = new WebSocket(`${wsUrl}/api/ws/events/${newSessionId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected for RAG integration');
      };
      
      ws.onmessage = async (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('Received message from backend:', message);
          
          // Handle function call results
          if (message.type === 'function_call_result') {
            const { call_id, function_name, result } = message;
            
            if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
              // Send function call output back to OpenAI
              if (result.success) {
                // Format the result for OpenAI
                let output = '';
                if (function_name === 'search_knowledge_base') {
                  if (result.context && result.context.trim()) {
                    output = JSON.stringify({
                      context: result.context,
                      sources: result.sources || [],
                      message: 'Knowledge base search completed successfully'
                    });
                  } else {
                    output = JSON.stringify({
                      context: '',
                      sources: [],
                      message: result.message || 'No relevant information found in knowledge base'
                    });
                  }
                } else {
                  output = JSON.stringify(result);
                }
                
                // Send function call output to OpenAI
                const functionOutput = {
                  type: 'conversation.item.create',
                  item: {
                    type: 'function_call_output',
                    call_id: call_id,
                    output: output
                  }
                };
                
                dataChannelRef.current.send(JSON.stringify(functionOutput));
                console.log('Sent function call result to OpenAI:', function_name);
                
                // Trigger response generation
                const responseCreate = {
                  type: 'response.create'
                };
                dataChannelRef.current.send(JSON.stringify(responseCreate));
              } else {
                // Send error result
                const errorOutput = {
                  type: 'conversation.item.create',
                  item: {
                    type: 'function_call_output',
                    call_id: call_id,
                    output: JSON.stringify({
                      error: result.error || 'Function execution failed'
                    })
                  }
                };
                dataChannelRef.current.send(JSON.stringify(errorOutput));
                
                // Still trigger response so model can handle the error
                const responseCreate = {
                  type: 'response.create'
                };
                dataChannelRef.current.send(JSON.stringify(responseCreate));
              }
            }
          } 
          // Keep backward compatibility for old rag_context messages (though shouldn't be used with function calling)
          else if (message.type === 'rag_context') {
            console.warn('Received rag_context message - this is the old approach. Function calling should be used instead.');
          } 
          else if (message.type === 'rag_error') {
            console.error('RAG service error:', message.error);
          } 
          else if (message.type === 'error') {
            console.error('Backend error:', message.error);
          }
        } catch (err) {
          console.error('Error processing WebSocket message:', err);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Don't fail the session if WebSocket fails - RAG is optional
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed');
      };
      
      websocketRef.current = ws;

    } catch (err) {
      console.error('Error starting session:', err);
      setError(err instanceof Error ? err.message : 'Failed to start session');
      setStatus('error');
      stopSession();
    }
  }, []);

  const stopSession = useCallback(() => {
    // Close WebSocket connection
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }

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
