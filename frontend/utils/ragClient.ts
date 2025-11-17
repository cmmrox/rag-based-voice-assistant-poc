/**
 * REST API client for RAG function calls
 * Replaces WebSocket-based communication with synchronous REST API calls
 */

import { BACKEND_URL } from '@/constants/api';
import { FUNCTION_CALL_TIMEOUT_MS } from '@/constants/timing';

/**
 * Request payload for RAG function call
 */
interface FunctionCallRequest {
  call_id: string;
  function_name: string;
  arguments: {
    query: string;
  };
}

/**
 * Result structure for RAG function execution
 */
interface FunctionCallResult {
  context: string;
  sources: Array<{
    source: string;
    content: string;
    metadata?: Record<string, any>;
  }>;
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Response structure from backend
 */
interface FunctionCallResponse {
  call_id: string;
  function_name: string;
  result: FunctionCallResult;
}

/**
 * Execute a RAG function call via REST API
 *
 * @param callId - Unique identifier for the function call
 * @param functionName - Name of the function to execute (e.g., "rag_knowledge")
 * @param args - Function arguments containing the query
 * @returns Promise resolving to the function call response
 * @throws Error if the request fails or times out
 */
export async function executeFunctionCall(
  callId: string,
  functionName: string,
  args: { query: string }
): Promise<FunctionCallResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FUNCTION_CALL_TIMEOUT_MS);

  try {
    const request: FunctionCallRequest = {
      call_id: callId,
      function_name: functionName,
      arguments: args,
    };

    console.log('[RAG Client] → Sending function call:', functionName, 'call_id:', callId);

    const response = await fetch(`${BACKEND_URL}/api/rag/function-call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data: FunctionCallResponse = await response.json();

    console.log(
      '[RAG Client] ← Function result received for call_id:',
      data.call_id,
      'success:',
      data.result.success
    );

    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error('[RAG Client] ✗ Function call timeout after', FUNCTION_CALL_TIMEOUT_MS, 'ms');
        throw new Error(`Function execution timeout after ${FUNCTION_CALL_TIMEOUT_MS / 1000} seconds`);
      }
      console.error('[RAG Client] ✗ Function call error:', error.message);
      throw error;
    }

    throw new Error('Unknown error during function call');
  }
}

/**
 * Format RAG result for sending to OpenAI
 * Converts the function call result into a JSON string for OpenAI
 *
 * @param result - The function call result from backend
 * @returns JSON string formatted for OpenAI function output
 */
export function formatRagResult(result: FunctionCallResult): string {
  if (!result.success) {
    return JSON.stringify({
      error: result.error || 'Unknown error occurred',
    });
  }

  return JSON.stringify({
    context: result.context,
    sources: result.sources,
    message: result.message || 'Successfully retrieved information from knowledge base',
  });
}
