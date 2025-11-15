/**
 * Utility functions for handling OpenAI function calls
 * Extracted from useVoiceSession.ts for better code organization
 */

import type { OpenAIEvent, FunctionCallEvent, FunctionCallOutputEvent, ResponseCreateEvent } from '@/types/openai';
import { FUNCTION_OUTPUT_DELAY_MS } from '@/constants/timing';

/**
 * Sends a function call output to OpenAI via the data channel
 *
 * @param dataChannel - The RTCDataChannel to send the output through
 * @param callId - The function call ID to respond to
 * @param output - The stringified output data
 * @returns The event_id of the sent output
 */
export function sendFunctionOutput(
  dataChannel: RTCDataChannel,
  callId: string,
  output: string
): string {
  const functionOutput: FunctionCallOutputEvent = {
    type: 'conversation.item.create',
    event_id: crypto.randomUUID(),
    item: {
      type: 'function_call_output',
      call_id: callId,
      output: output,
    },
  };

  dataChannel.send(JSON.stringify(functionOutput));
  console.log('[RAG] → Sent function_call_output to OpenAI, event_id:', functionOutput.event_id);

  return functionOutput.event_id;
}

/**
 * Creates a new response after sending function output
 * This is critical because the original response completes before function results return
 *
 * @param dataChannel - The RTCDataChannel to send the response.create through
 * @param delay - Optional delay in milliseconds before creating the response (default from constants)
 */
export function createNewResponse(
  dataChannel: RTCDataChannel,
  delay: number = FUNCTION_OUTPUT_DELAY_MS
): void {
  setTimeout(() => {
    if (dataChannel.readyState === 'open') {
      const responseCreate: ResponseCreateEvent = {
        type: 'response.create',
        event_id: crypto.randomUUID(),
      };
      dataChannel.send(JSON.stringify(responseCreate));
      console.log('[RAG] → Created new response, event_id:', responseCreate.event_id);
    }
  }, delay);
}

/**
 * Extracts the call_id from a function call event
 * Different event types use different field names (call_id, id, item_id)
 *
 * @param functionCall - The function call event object
 * @returns The extracted call_id or null if not found
 */
export function extractCallId(functionCall: any): string | null {
  const callId = functionCall.call_id || functionCall.id || functionCall.item_id;

  if (!callId) {
    console.error('[RAG] ✗ No call_id found in function call:', functionCall);
    console.error('[RAG] Available fields:', Object.keys(functionCall));
    return null;
  }

  console.log(
    '[RAG] ✓ Extracted call_id:',
    callId,
    'from field:',
    functionCall.call_id ? 'call_id' : functionCall.id ? 'id' : 'item_id'
  );

  return callId;
}

/**
 * Parses function arguments from string or object format
 *
 * @param args - The arguments (string or object)
 * @returns Parsed arguments object or empty object on error
 */
export function parseFunctionArguments(args: any): Record<string, any> {
  try {
    if (typeof args === 'string') {
      return JSON.parse(args);
    } else if (args && typeof args === 'object') {
      return args;
    }
    return {};
  } catch (error) {
    console.error('[RAG] ✗ Error parsing function arguments:', error);
    console.error('[RAG] ✗ Raw arguments:', args);
    return {};
  }
}

/**
 * Validates that function arguments are not empty
 *
 * @param args - The parsed arguments object
 * @returns true if arguments are valid and not empty
 */
export function validateFunctionArguments(args: Record<string, any>): boolean {
  if (!args || Object.keys(args).length === 0) {
    console.error('[RAG] ✗ Arguments are empty, cannot execute function');
    return false;
  }
  console.log('[RAG] ✓ Parsed arguments:', args);
  return true;
}

/**
 * Formats RAG function result for OpenAI
 *
 * @param result - The result from the RAG backend
 * @returns Stringified output for OpenAI
 */
export function formatRagResult(result: any): string {
  if (result.success) {
    if (result.context && result.context.trim()) {
      console.log('[RAG] ✓ Retrieved context, length:', result.context.length);
      return JSON.stringify({
        context: result.context,
        sources: result.sources || [],
        message: 'RAG knowledge retrieval completed successfully',
      });
    } else {
      console.log('[RAG] ⚠ No context found');
      return JSON.stringify({
        context: '',
        sources: [],
        message: result.message || 'No relevant information found in RAG knowledge base',
      });
    }
  } else {
    return JSON.stringify({
      error: result.error || 'Function execution failed',
    });
  }
}
