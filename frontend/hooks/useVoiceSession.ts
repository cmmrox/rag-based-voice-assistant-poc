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
import type { SessionStatus, TranscriptMessage } from '@/types/session';
import type { OpenAIEvent } from '@/types/openai';
import { BACKEND_URL, OPENAI_MODEL } from '@/constants/api';
import { RAG_KNOWLEDGE_TOOL } from '@/constants/tools';
import {
  FUNCTION_OUTPUT_DELAY_MS,
  FUNCTION_CALL_TIMEOUT_MS,
  EVENT_PROCESSING_DELAY_MS,
} from '@/constants/timing';
import {
  sendFunctionOutput,
  createNewResponse,
  extractCallId,
  parseFunctionArguments,
  validateFunctionArguments,
  formatRagResult,
} from '@/utils/functionCalls';
import {
  createAudioElement,
  handleIncomingTrack,
  getUserAudioStream,
  addAudioTracks,
  stopMediaStream,
  stopAudioPlayback,
} from '@/utils/webrtc';
import { generateWebSocketUrl, sendFunctionCallToBackend } from '@/utils/websocket';

/**
 * Custom hook for managing OpenAI Realtime API voice sessions
 *
 * Provides complete lifecycle management for voice assistant sessions including:
 * - WebRTC connection setup and teardown
 * - Audio stream management (microphone input and speaker output)
 * - OpenAI event handling via data channel
 * - RAG function calling integration via WebSocket
 * - Session state management and error handling
 *
 * @returns Object containing session state and control functions
 */
export function useVoiceSession() {
  // Session state
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // WebRTC and connection refs
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);

  // Function call management refs
  const functionRegisteredRef = useRef<boolean>(false);
  const processedCallIdsRef = useRef<Set<string>>(new Set());
  const functionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Adds a message to the transcript
   *
   * @param role - The role of the message sender (user or assistant)
   * @param text - The message text content
   */
  const addTranscriptMessage = useCallback((role: 'user' | 'assistant', text: string) => {
    setTranscript((prev) => [
      ...prev,
      {
        role,
        text,
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  /**
   * Handles function call detection and execution
   * Implements comprehensive detection across multiple OpenAI event types
   *
   * @param eventData - The OpenAI event that may contain a function call
   */
  const handleFunctionCall = useCallback(
    (eventData: any) => {
      let detectedFunctionCall = null;

      // Check 0: response.function_call_arguments.done (HIGHEST PRIORITY - EARLIEST DETECTION)
      // This fires when arguments are complete but BEFORE response.done
      // Critical for avoiding "Tool call ID not found" error
      if (eventData.type === 'response.function_call_arguments.done') {
        if (eventData.name === 'rag_knowledge') {
          // CRITICAL: Validate that arguments are complete and valid JSON before processing
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
                  parsed: parsedArgs,
                });
                detectedFunctionCall = eventData;
              } else {
                console.log('[RAG] ⚠ Arguments are empty, will use fallback detection at response.done');
              }
            } else {
              console.log('[RAG] ⚠ Arguments not ready yet, will use fallback detection at response.done');
            }
          } catch (parseError: any) {
            console.warn('[RAG] ⚠ Arguments not valid JSON yet, will use fallback detection at response.done');
            console.warn('[RAG] Invalid arguments:', eventData.arguments);
            console.warn('[RAG] Parse error:', parseError.message);
          }
        }
      }

      // Check 1: response.done with response.output array (FALLBACK)
      if (!detectedFunctionCall && eventData.type === 'response.done' && eventData.response?.output) {
        console.log('[RAG] Checking response.done with output array');
        for (const output of eventData.response.output) {
          if (output.type === 'function_call' && output.name === 'rag_knowledge') {
            console.log('[RAG] ✓ Found function call in response.done.output');
            detectedFunctionCall = output;
            break;
          }
        }
      }

      // Check 2: response.function_call event
      if (!detectedFunctionCall && eventData.type === 'response.function_call') {
        if (eventData.name === 'rag_knowledge') {
          console.log('[RAG] ✓ Found function call in response.function_call event');
          detectedFunctionCall = eventData;
        }
      }

      // Check 3: response.function_call.done event
      if (!detectedFunctionCall && eventData.type === 'response.function_call.done') {
        if (eventData.function_call && eventData.function_call.name === 'rag_knowledge') {
          console.log('[RAG] ✓ Found function call in response.function_call.done');
          detectedFunctionCall = eventData.function_call;
        }
      }

      // Check 4: function_call nested in response
      if (!detectedFunctionCall && eventData.response && eventData.response.function_call) {
        const funcCall = eventData.response.function_call;
        if (funcCall.name === 'rag_knowledge') {
          console.log('[RAG] ✓ Found function call nested in response');
          detectedFunctionCall = funcCall;
        }
      }

      // Check 5: conversation.item.completed with function_call item
      if (!detectedFunctionCall && eventData.type === 'conversation.item.completed') {
        const item = eventData.item;
        if (item && item.type === 'function_call' && item.name === 'rag_knowledge') {
          console.log('[RAG] ✓ Found function call in conversation.item.completed');
          detectedFunctionCall = item;
        }
      }

      // Check 6: conversation.updated with function_call item
      if (!detectedFunctionCall && eventData.type === 'conversation.updated') {
        const item = eventData.item;
        if (item && item.type === 'function_call' && item.name === 'rag_knowledge') {
          // Check if function call is complete (has all arguments)
          if (
            item.status === 'completed' ||
            (item.arguments && typeof item.arguments === 'string' && item.arguments.length > 0)
          ) {
            console.log('[RAG] ✓ Found completed function call in conversation.updated');
            detectedFunctionCall = item;
          }
        }
      }

      // Handle detected function call
      if (detectedFunctionCall) {
        const callId = extractCallId(detectedFunctionCall);

        if (!callId) {
          return;
        }

        // Deduplication: Check if we've already processed this call_id
        if (processedCallIdsRef.current.has(callId)) {
          console.log('[RAG] ⊘ Already processed call_id:', callId, '- skipping');
          return;
        }

        // Mark as processed
        processedCallIdsRef.current.add(callId);
        console.log('[RAG] Processing function call with call_id:', callId);
        setStatus('processing');

        // Parse function arguments
        const functionArgs = parseFunctionArguments(detectedFunctionCall.arguments);

        // Validate arguments are not empty before sending to backend
        if (!validateFunctionArguments(functionArgs)) {
          console.error('[RAG] ✗ Skipping backend call');
          // Remove from processed set so it can be retried if response.done provides valid args
          processedCallIdsRef.current.delete(callId);
          return;
        }

        // Send function call to backend for execution
        if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
          sendFunctionCallToBackend(
            websocketRef.current,
            callId,
            detectedFunctionCall.name,
            functionArgs
          );

          // Set timeout for function execution
          if (functionTimeoutRef.current) {
            clearTimeout(functionTimeoutRef.current);
          }

          functionTimeoutRef.current = setTimeout(() => {
            console.error('[RAG] ✗ Function execution timeout for call_id:', callId);

            // Send error response to OpenAI
            if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
              const errorOutput = JSON.stringify({
                error: 'Function execution timeout after 30 seconds',
              });

              sendFunctionOutput(dataChannelRef.current, callId, errorOutput);
              createNewResponse(dataChannelRef.current);
            }
          }, FUNCTION_CALL_TIMEOUT_MS);
        } else {
          console.error('[RAG] ✗ WebSocket not available for function call execution');
        }
      }
    },
    []
  );

  /**
   * Handles incoming OpenAI events from the data channel
   *
   * @param event - The message event from the data channel
   */
  const handleDataChannelMessage = useCallback(
    async (event: MessageEvent) => {
      try {
        const eventData = JSON.parse(event.data);
        console.log('Received event from OpenAI:', eventData);

        // Handle session.created - register function after session is created
        if (eventData.type === 'session.created' && !functionRegisteredRef.current) {
          console.log('[RAG] Session created, registering rag_knowledge function');

          // Small delay to ensure data channel is fully ready
          setTimeout(() => {
            if (dataChannelRef.current && dataChannelRef.current.readyState === 'open') {
              const sessionUpdate = {
                type: 'session.update',
                event_id: crypto.randomUUID(),
                session: {
                  type: 'realtime',
                  tools: [RAG_KNOWLEDGE_TOOL],
                  tool_choice: 'auto',
                },
              };
              dataChannelRef.current.send(JSON.stringify(sessionUpdate));
              functionRegisteredRef.current = true;
              console.log('[RAG] Function registered successfully with event_id:', sessionUpdate.event_id);
            } else {
              console.warn('[RAG] Data channel not open when session.created received');
            }
          }, EVENT_PROCESSING_DELAY_MS);
        }

        // Handle user audio transcription
        if (eventData.type === 'conversation.item.input_audio_transcription.completed') {
          const transcriptText = eventData.transcript || '';
          addTranscriptMessage('user', transcriptText);
          setStatus('processing');
        }
        // Handle function calls
        else {
          handleFunctionCall(eventData);
        }

        // Handle assistant audio transcript
        if (eventData.type === 'response.audio_transcript.delta') {
          const delta = eventData.delta || '';
          if (delta) {
            addTranscriptMessage('assistant', delta);
            setStatus('speaking');
          }
        } else if (eventData.type === 'response.done') {
          setStatus('listening');
        } else if (eventData.type === 'error') {
          setError(eventData.error?.message || 'Unknown error');
          setStatus('error');
        }
      } catch (err) {
        console.error('Error parsing event:', err);
      }
    },
    [addTranscriptMessage, handleFunctionCall]
  );

  /**
   * Handles WebSocket messages from the backend (RAG function results)
   *
   * @param event - The message event from the WebSocket
   */
  const handleWebSocketMessage = useCallback(async (event: MessageEvent) => {
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
          // Format the result for OpenAI
          const output = formatRagResult(result);

          // Send function call output to OpenAI
          sendFunctionOutput(dataChannelRef.current, call_id, output);

          // Create NEW response to use the function output
          createNewResponse(dataChannelRef.current, FUNCTION_OUTPUT_DELAY_MS);
        }
      } else if (message.type === 'rag_error') {
        console.error('[RAG] ✗ RAG service error:', message.error);
      } else if (message.type === 'error') {
        console.error('[Backend] ✗ Error:', message.error);
      }
    } catch (err) {
      console.error('[WebSocket] ✗ Error processing message:', err);
    }
  }, []);

  /**
   * Starts a new voice session
   * Sets up WebRTC connection, audio streams, data channel, and WebSocket
   */
  const startSession = useCallback(async () => {
    try {
      setStatus('connecting');
      setError(null);

      // Get user media (microphone)
      const stream = await getUserAudioStream();
      localStreamRef.current = stream;

      // Create peer connection (no STUN servers needed for OpenAI)
      const peerConnection = new RTCPeerConnection();
      peerConnectionRef.current = peerConnection;

      // Set up audio element for playback
      const audioElement = createAudioElement();
      audioElementRef.current = audioElement;

      peerConnection.ontrack = (event) => {
        handleIncomingTrack(event, audioElement);
      };

      // Add local audio track for microphone input
      addAudioTracks(peerConnection, stream);

      // Set up data channel for sending and receiving events
      const dataChannel = peerConnection.createDataChannel('oai-events');
      dataChannelRef.current = dataChannel;

      // Listen for server events from OpenAI
      dataChannel.onmessage = handleDataChannelMessage;

      dataChannel.onopen = () => {
        console.log('Data channel opened');
        setStatus('listening');
      };

      dataChannel.onerror = (err) => {
        console.error('Data channel error:', err);
        setError('Data channel error');
        setStatus('error');
      };

      // Handle connection state changes
      peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', peerConnection.connectionState);
        if (peerConnection.connectionState === 'connected') {
          setStatus('listening');
        } else if (
          peerConnection.connectionState === 'failed' ||
          peerConnection.connectionState === 'disconnected'
        ) {
          setStatus('error');
          setError('Connection failed');
        }
      };

      // Create offer and send to backend
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);

      // POST SDP to backend endpoint which forwards to OpenAI
      const sdpResponse = await fetch(`${BACKEND_URL}/api/realtime/session`, {
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

      await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));

      // Generate a session ID for tracking
      const newSessionId = crypto.randomUUID();
      setSessionId(newSessionId);

      // Connect to backend WebSocket for RAG integration
      const websocketUrl = generateWebSocketUrl(BACKEND_URL, newSessionId);
      const websocket = new WebSocket(websocketUrl);

      websocket.onopen = () => {
        console.log('WebSocket connected for RAG integration');
      };

      websocket.onmessage = handleWebSocketMessage;

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Don't fail the session if WebSocket fails - RAG is optional
      };

      websocket.onclose = () => {
        console.log('WebSocket closed');
      };

      websocketRef.current = websocket;
    } catch (err) {
      console.error('Error starting session:', err);
      setError(err instanceof Error ? err.message : 'Failed to start session');
      setStatus('error');
      stopSession();
    }
  }, [handleDataChannelMessage, handleWebSocketMessage]);

  /**
   * Stops the current voice session
   * Closes all connections and cleans up resources
   */
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
    stopMediaStream(localStreamRef.current);
    localStreamRef.current = null;

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
    stopAudioPlayback(audioElementRef.current);
    audioElementRef.current = null;

    // Reset state
    setStatus('idle');
    setSessionId(null);
    setError(null);
    functionRegisteredRef.current = false;
    processedCallIdsRef.current.clear();

    console.log('[Session] ✓ Session stopped');
  }, []);

  return {
    status,
    transcript,
    error,
    sessionId,
    startSession,
    stopSession,
  };
}
