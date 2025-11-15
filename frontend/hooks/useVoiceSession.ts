'use client';

/**
 * OpenAI Realtime API Voice Session Hook
 *
 * CRITICAL FIXES IMPLEMENTED (based on openai-realtime-console reference):
 *
 * 1. EVENT_ID GENERATION: All events sent to OpenAI now include event_id (crypto.randomUUID())
 *    - This is REQUIRED for OpenAI to properly process events
 *    - Missing event_ids cause events to be silently ignored
 *
 * 2. EARLY FUNCTION CALL DETECTION: Detects at response.function_call_arguments.done (CRITICAL!)
 *    - This event fires when arguments are ready but BEFORE response.done
 *    - Prevents "Tool call ID not found in conversation" error
 *    - By detecting early, we can send function_call_output while item_id is still valid
 *    - Fallback checks: response.done, response.function_call, conversation.item.completed, etc.
 *
 * 3. ROBUST CALL_ID EXTRACTION: Prioritizes call_id field (CRITICAL!)
 *    - call_id is the actual function call ID (required for function_call_output)
 *    - item_id is the conversation item ID (different from call_id)
 *    - Priority: call_id > id > item_id (as last resort)
 *    - Deduplication prevents processing same call multiple times
 *
 * 4. NEW RESPONSE CREATION AFTER FUNCTION OUTPUT: response.create with delay
 *    - Due to backend latency, original response completes (response.done) before function result returns
 *    - After sending function_call_output, we create a NEW response to use that output
 *    - 100ms delay ensures function_call_output is processed before new response starts
 *    - This is different from "active response" error - that response has already completed
 *
 * 5. TIMEOUT HANDLING: 30-second timeout for function execution
 *    - Prevents hanging if backend doesn't respond
 *    - Automatically sends error to OpenAI on timeout
 *
 * 6. COMPREHENSIVE LOGGING: Detailed logs with symbols (✓, ✗, →, ←, ⊘)
 *    - Makes debugging much easier
 *    - Tracks entire event flow
 *    - Shows which field (item_id/call_id/id) was used for call_id
 */

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
  const processedCallIdsRef = useRef<Set<string>>(new Set());
  const functionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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

            // Small delay to ensure data channel is fully ready (following reference implementation pattern)
            setTimeout(() => {
              if (dc.readyState === 'open') {
                const sessionUpdate = {
                  type: 'session.update',
                  event_id: crypto.randomUUID(),
                  session: {
                    type: 'realtime',
                    tools: [ragKnowledgeTool],
                    tool_choice: 'auto'
                  }
                };
                dc.send(JSON.stringify(sessionUpdate));
                functionRegisteredRef.current = true;
                setFunctionRegistered(true);
                console.log('[RAG] Function registered successfully with event_id:', sessionUpdate.event_id);
              } else {
                console.warn('[RAG] Data channel not open when session.created received');
              }
            }, 100);
          }
          
          // Handle different event types
          if (eventData.type === 'conversation.item.input_audio_transcription.completed') {
            const transcript = eventData.transcript || '';
            addTranscriptMessage('user', transcript);
            setStatus('processing');
          }
          // Comprehensive function call detection (following reference implementation patterns)
          else {
            let foundFunctionCall = null;

            // Check 0: response.function_call_arguments.done (HIGHEST PRIORITY - EARLIEST DETECTION)
            // This fires when arguments are complete but BEFORE response.done
            // Critical for avoiding "Tool call ID not found" error
            if (eventData.type === 'response.function_call_arguments.done') {
              if (eventData.name === 'rag_knowledge') {
                // CRITICAL: Validate that arguments are complete and valid JSON before processing
                // Sometimes this event fires with incomplete/malformed arguments
                try {
                  if (eventData.arguments && typeof eventData.arguments === 'string') {
                    const parsedArgs = JSON.parse(eventData.arguments);

                    // Verify arguments are not empty and have required fields
                    if (parsedArgs && Object.keys(parsedArgs).length > 0) {
                      console.log('[RAG] ✓✓✓ Found function call with VALID arguments (EARLY DETECTION)');
                      console.log('[RAG] Event details:', {
                        item_id: eventData.item_id,
                        name: eventData.name,
                        call_id: eventData.call_id,
                        arguments: eventData.arguments,
                        parsed: parsedArgs
                      });
                      foundFunctionCall = eventData;
                    } else {
                      console.log('[RAG] ⚠ Arguments are empty, will use fallback detection at response.done');
                    }
                  } else {
                    console.log('[RAG] ⚠ Arguments not ready yet, will use fallback detection at response.done');
                  }
                } catch (parseError) {
                  console.warn('[RAG] ⚠ Arguments not valid JSON yet, will use fallback detection at response.done');
                  console.warn('[RAG] Invalid arguments:', eventData.arguments);
                  console.warn('[RAG] Parse error:', parseError.message);
                  // Don't set foundFunctionCall - let response.done handle it with complete arguments
                }
              }
            }

            // Check 1: response.done with response.output array (FALLBACK)
            if (!foundFunctionCall && eventData.type === 'response.done' && eventData.response?.output) {
              console.log('[RAG] Checking response.done with output array');
              for (const output of eventData.response.output) {
                if (output.type === 'function_call' && output.name === 'rag_knowledge') {
                  console.log('[RAG] ✓ Found function call in response.done.output');
                  foundFunctionCall = output;
                  break;
                }
              }
            }

            // Check 2: response.function_call event (NEW - from reference implementation)
            if (!foundFunctionCall && eventData.type === 'response.function_call') {
              if (eventData.name === 'rag_knowledge') {
                console.log('[RAG] ✓ Found function call in response.function_call event');
                foundFunctionCall = eventData;
              }
            }

            // Check 3: response.function_call.done event (NEW - from reference implementation)
            if (!foundFunctionCall && eventData.type === 'response.function_call.done') {
              if (eventData.function_call && eventData.function_call.name === 'rag_knowledge') {
                console.log('[RAG] ✓ Found function call in response.function_call.done');
                foundFunctionCall = eventData.function_call;
              }
            }

            // Check 4: function_call nested in response (NEW - from reference implementation)
            if (!foundFunctionCall && eventData.response && eventData.response.function_call) {
              const funcCall = eventData.response.function_call;
              if (funcCall.name === 'rag_knowledge') {
                console.log('[RAG] ✓ Found function call nested in response');
                foundFunctionCall = funcCall;
              }
            }

            // Check 5: conversation.item.completed with function_call item
            if (!foundFunctionCall && eventData.type === 'conversation.item.completed') {
              const item = eventData.item;
              if (item && item.type === 'function_call' && item.name === 'rag_knowledge') {
                console.log('[RAG] ✓ Found function call in conversation.item.completed');
                foundFunctionCall = item;
              }
            }

            // Check 6: conversation.updated with function_call item
            if (!foundFunctionCall && eventData.type === 'conversation.updated') {
              const item = eventData.item;
              if (item && item.type === 'function_call' && item.name === 'rag_knowledge') {
                // Check if function call is complete (has all arguments)
                if (item.status === 'completed' || (item.arguments && typeof item.arguments === 'string' && item.arguments.length > 0)) {
                  console.log('[RAG] ✓ Found completed function call in conversation.updated');
                  foundFunctionCall = item;
                }
              }
            }
            
            // Handle detected function call
            if (foundFunctionCall) {
              // Extract call_id robustly (different event types use different field names)
              // CRITICAL: Use call_id field first (actual function call ID)
              // item_id is the conversation item ID, NOT the function call ID
              const call_id = foundFunctionCall.call_id || foundFunctionCall.id || foundFunctionCall.item_id;

              if (!call_id) {
                console.error('[RAG] ✗ No call_id found in function call:', foundFunctionCall);
                console.error('[RAG] Available fields:', Object.keys(foundFunctionCall));
                return;
              }

              console.log('[RAG] ✓ Extracted call_id:', call_id, 'from field:',
                foundFunctionCall.call_id ? 'call_id' :
                foundFunctionCall.id ? 'id' : 'item_id');

              // Deduplication: Check if we've already processed this call_id
              if (processedCallIdsRef.current.has(call_id)) {
                console.log('[RAG] ⊘ Already processed call_id:', call_id, '- skipping');
                return;
              }

              // Mark as processed
              processedCallIdsRef.current.add(call_id);
              console.log('[RAG] Processing function call with call_id:', call_id);
              setStatus('processing');

              // Parse function arguments (they might come as a string)
              let functionArgs = {};
              try {
                if (typeof foundFunctionCall.arguments === 'string') {
                  functionArgs = JSON.parse(foundFunctionCall.arguments);
                } else if (foundFunctionCall.arguments) {
                  functionArgs = foundFunctionCall.arguments;
                }
                console.log('[RAG] ✓ Parsed arguments:', functionArgs);
              } catch (e) {
                console.error('[RAG] ✗ Error parsing function arguments:', e.message);
                console.error('[RAG] ✗ Raw arguments string:', foundFunctionCall.arguments);
                console.error('[RAG] ✗ This should not happen if early detection validation worked');
                functionArgs = {};
              }

              // Validate arguments are not empty before sending to backend
              if (!functionArgs || Object.keys(functionArgs).length === 0) {
                console.error('[RAG] ✗ Arguments are empty, cannot execute function');
                console.error('[RAG] ✗ Skipping backend call');
                // Remove from processed set so it can be retried if response.done provides valid args
                processedCallIdsRef.current.delete(call_id);
                return;
              }

              // Send function call to backend for execution
              if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
                websocketRef.current.send(JSON.stringify({
                  type: 'function_call',
                  call_id: call_id,
                  function_name: foundFunctionCall.name,
                  arguments: functionArgs
                }));
                console.log('[RAG] → Sent function call to backend:', foundFunctionCall.name, 'call_id:', call_id);

                // Set timeout for function execution (30 seconds)
                if (functionTimeoutRef.current) {
                  clearTimeout(functionTimeoutRef.current);
                }
                functionTimeoutRef.current = setTimeout(() => {
                  console.error('[RAG] ✗ Function execution timeout for call_id:', call_id);
                  // Send error response to OpenAI
                  if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
                    const errorOutput = {
                      type: 'conversation.item.create',
                      event_id: crypto.randomUUID(),
                      item: {
                        type: 'function_call_output',
                        call_id: call_id,
                        output: JSON.stringify({
                          error: 'Function execution timeout after 30 seconds'
                        })
                      }
                    };
                    dataChannelRef.current.send(JSON.stringify(errorOutput));
                    console.log('[RAG] → Sent timeout error to OpenAI');

                    // Create NEW response to handle the timeout error
                    setTimeout(() => {
                      if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
                        const responseCreate = {
                          type: 'response.create',
                          event_id: crypto.randomUUID()
                        };
                        dataChannelRef.current.send(JSON.stringify(responseCreate));
                        console.log('[RAG] → Created new response to handle timeout error');
                      }
                    }, 100);
                  }
                }, 30000);
              } else {
                console.error('[RAG] ✗ WebSocket not available for function call execution');
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
          console.log('[WebSocket] ← Received from backend:', message.type);

          // Handle function call results
          if (message.type === 'function_call_result') {
            const { call_id, function_name, result } = message;

            // Clear timeout since we got a response
            if (functionTimeoutRef.current) {
              clearTimeout(functionTimeoutRef.current);
              functionTimeoutRef.current = null;
            }

            console.log('[RAG] ← Function result received for call_id:', call_id);

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
                    console.log('[RAG] ✓ Retrieved context, length:', result.context.length);
                  } else {
                    output = JSON.stringify({
                      context: '',
                      sources: [],
                      message: result.message || 'No relevant information found in RAG knowledge base'
                    });
                    console.log('[RAG] ⚠ No context found');
                  }
                } else {
                  output = JSON.stringify(result);
                }

                // CRITICAL: Send function call output with event_id
                const functionOutput = {
                  type: 'conversation.item.create',
                  event_id: crypto.randomUUID(), // CRITICAL: event_id required!
                  item: {
                    type: 'function_call_output',
                    call_id: call_id,
                    output: output
                  }
                };

                dataChannelRef.current.send(JSON.stringify(functionOutput));
                console.log('[RAG] → Sent function_call_output to OpenAI, event_id:', functionOutput.event_id);

                // CRITICAL: Create NEW response to use the function output
                // Due to backend latency, the original response has already completed (response.done)
                // We need to explicitly create a new response that will use the function_call_output
                setTimeout(() => {
                  if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
                    const responseCreate = {
                      type: 'response.create',
                      event_id: crypto.randomUUID()
                    };
                    dataChannelRef.current.send(JSON.stringify(responseCreate));
                    console.log('[RAG] → Created new response to use function output, event_id:', responseCreate.event_id);
                  }
                }, 100); // Small delay to ensure function_call_output is processed first
              } else {
                // Send error result with event_id
                const errorOutput = {
                  type: 'conversation.item.create',
                  event_id: crypto.randomUUID(), // CRITICAL: event_id required!
                  item: {
                    type: 'function_call_output',
                    call_id: call_id,
                    output: JSON.stringify({
                      error: result.error || 'Function execution failed'
                    })
                  }
                };
                dataChannelRef.current.send(JSON.stringify(errorOutput));
                console.log('[RAG] → Sent error output to OpenAI, event_id:', errorOutput.event_id);

                // Create NEW response to handle the error
                setTimeout(() => {
                  if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
                    const responseCreate = {
                      type: 'response.create',
                      event_id: crypto.randomUUID()
                    };
                    dataChannelRef.current.send(JSON.stringify(responseCreate));
                    console.log('[RAG] → Created new response to handle error, event_id:', responseCreate.event_id);
                  }
                }, 100);
              }
            }
          }
          else if (message.type === 'rag_error') {
            console.error('[RAG] ✗ RAG service error:', message.error);
          }
          else if (message.type === 'error') {
            console.error('[Backend] ✗ Error:', message.error);
          }
        } catch (err) {
          console.error('[WebSocket] ✗ Error processing message:', err);
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
    console.log('[Session] Stopping session...');

    // Clear function timeout
    if (functionTimeoutRef.current) {
      clearTimeout(functionTimeoutRef.current);
      functionTimeoutRef.current = null;
    }

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

    // Reset state
    setStatus('idle');
    setSessionId(null);
    setError(null);
    setFunctionRegistered(false);
    setEvents([]);
    functionRegisteredRef.current = false;
    processedCallIdsRef.current.clear();

    console.log('[Session] ✓ Session stopped');
  }, []);

  // Helper function to send events with automatic event_id generation
  const sendEvent = useCallback((event: any) => {
    if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
      // Add event_id if not present (critical for OpenAI to process events correctly)
      const eventWithId = {
        ...event,
        event_id: event.event_id || crypto.randomUUID()
      };
      dataChannelRef.current.send(JSON.stringify(eventWithId));
      console.log('[Event] Sent to OpenAI:', eventWithId.type, 'event_id:', eventWithId.event_id);
    } else {
      console.warn('[Event] Data channel not open, cannot send event');
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
