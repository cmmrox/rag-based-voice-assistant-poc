'use client';

import { useState, useRef, useCallback } from 'react';

export type SessionStatus = 'idle' | 'connecting' | 'connected' | 'listening' | 'processing' | 'speaking' | 'error';

export interface TranscriptMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

// RAG Knowledge function definition - defined directly in frontend to avoid CORS header issues
const ragKnowledgeTool = {
  type: 'function',
  name: 'rag_knowledge',
  description: 'Retrieve information from the RAG (Retrieval-Augmented Generation) knowledge base. Use this function when you need specific information from documents, knowledge base, or when the user asks questions that require information retrieval from stored knowledge.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The search query to find relevant information from the RAG knowledge base'
      }
    },
    required: ['query']
  }
};

export function useVoiceSession() {
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [functionRegistered, setFunctionRegistered] = useState(false);
  const [events, setEvents] = useState<any[]>([]);

  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const functionRegisteredRef = useRef<boolean>(false);

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

      // Listen for server events from OpenAI
      dc.onmessage = async (event) => {
        try {
          const eventData = JSON.parse(event.data);
          console.log('Received event from OpenAI:', eventData);
          
          // Store all events for comprehensive function call detection
          setEvents(prev => [eventData, ...prev]);
          
          // Handle session.created - register function after session is created
          if (eventData.type === 'session.created' && !functionRegisteredRef.current) {
            console.log('[RAG] Session created, registering rag_knowledge function');
            
            if (dc.readyState === 'open') {
              const sessionUpdate = {
                type: 'session.update',
                session: {
                  type: 'realtime',
                  tools: [ragKnowledgeTool],
                  tool_choice: 'auto'
                }
              };
              dc.send(JSON.stringify(sessionUpdate));
              functionRegisteredRef.current = true;
              setFunctionRegistered(true);
              console.log('[RAG] Function registered successfully');
            } else {
              console.warn('[RAG] Data channel not open when session.created received');
            }
          }
          
          // Handle different event types
          if (eventData.type === 'conversation.item.input_audio_transcription.completed') {
            const transcript = eventData.transcript || '';
            addTranscriptMessage('user', transcript);
            setStatus('processing');
            // Note: With function calling, RAG queries are handled via function calls
            // No need to manually trigger RAG query here
          } 
          // Comprehensive function call detection
          else {
            let foundFunctionCall = null;
            
            // Check 1: response.done with response.output array
            if (eventData.type === 'response.done' && eventData.response?.output) {
              console.log('[RAG] Checking response.done with output array');
              for (const output of eventData.response.output) {
                if (output.type === 'function_call' && output.name === 'rag_knowledge') {
                  console.log('[RAG] Found function call in response.done.output:', output);
                  foundFunctionCall = output;
                  break;
                }
              }
            }
            
            // Check 2: conversation.item.completed with function_call item
            if (!foundFunctionCall && eventData.type === 'conversation.item.completed') {
              const item = eventData.item;
              if (item && item.type === 'function_call' && item.name === 'rag_knowledge') {
                console.log('[RAG] Found function call in conversation.item.completed:', item);
                foundFunctionCall = item;
              }
            }
            
            // Check 3: conversation.updated with function_call item
            if (!foundFunctionCall && eventData.type === 'conversation.updated') {
              const item = eventData.item;
              if (item && item.type === 'function_call' && item.name === 'rag_knowledge') {
                // Check if function call is complete (has all arguments)
                if (item.status === 'completed' || (item.arguments && typeof item.arguments === 'string' && item.arguments.length > 0)) {
                  console.log('[RAG] Found completed function call in conversation.updated:', item);
                  foundFunctionCall = item;
                }
              }
            }
            
            // Handle detected function call
            if (foundFunctionCall) {
              console.log('[RAG] Processing function call:', foundFunctionCall);
              setStatus('processing');
              
              // Parse function arguments (they might come as a string)
              let functionArgs = {};
              try {
                if (typeof foundFunctionCall.arguments === 'string') {
                  functionArgs = JSON.parse(foundFunctionCall.arguments);
                } else if (foundFunctionCall.arguments) {
                  functionArgs = foundFunctionCall.arguments;
                }
              } catch (e) {
                console.error('[RAG] Error parsing function arguments:', e);
                functionArgs = {};
              }
              
              // Send function call to backend for execution
              if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
                websocketRef.current.send(JSON.stringify({
                  type: 'function_call',
                  call_id: foundFunctionCall.id || foundFunctionCall.call_id,
                  function_name: foundFunctionCall.name,
                  arguments: functionArgs
                }));
                console.log('[RAG] Sent function call to backend:', foundFunctionCall.name);
              } else {
                console.error('[RAG] WebSocket not available for function call execution');
              }
            }
          }
          
          // Handle other event types
          if (eventData.type === 'response.audio_transcript.delta') {
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
        // Note: Function registration will happen after session.created event
        // Do not send session config immediately - wait for session.created
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
      
      // Note: Session config (tools) is defined directly in frontend to avoid CORS header issues
      // Function will be registered after session.created event is received
      
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
                if (function_name === 'rag_knowledge') {
                  if (result.context && result.context.trim()) {
                    output = JSON.stringify({
                      context: result.context,
                      sources: result.sources || [],
                      message: 'RAG knowledge retrieval completed successfully'
                    });
                  } else {
                    output = JSON.stringify({
                      context: '',
                      sources: [],
                      message: result.message || 'No relevant information found in RAG knowledge base'
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
    setFunctionRegistered(false);
    setEvents([]);
    functionRegisteredRef.current = false;
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
