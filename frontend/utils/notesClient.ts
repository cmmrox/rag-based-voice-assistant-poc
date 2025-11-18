/**
 * REST API client for notes function calls
 */

import { BACKEND_URL } from '@/constants/api';
import { FUNCTION_CALL_TIMEOUT_MS } from '@/constants/timing';

/**
 * Arguments structure for notes management
 */
interface NotesArguments {
  action: 'create' | 'list' | 'search' | 'update' | 'delete';
  title?: string;
  content?: string;
  note_id?: string;
  query?: string;
}

/**
 * Request payload for notes function call
 */
interface NotesFunctionRequest {
  call_id: string;
  function_name: string;
  arguments: NotesArguments;
}

/**
 * Note object structure
 */
export interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

/**
 * Data wrapper for notes result
 */
interface NotesData {
  notes: Note[];
  count: number;
}

/**
 * Result structure for notes function execution
 */
interface NotesFunctionResult {
  success: boolean;
  message: string;
  data?: NotesData;
  error?: string;
}

/**
 * Response structure from backend
 */
export interface NotesFunctionResponse {
  call_id: string;
  function_name: string;
  result: NotesFunctionResult;
}

/**
 * Execute a notes function call via REST API
 *
 * @param callId - Unique identifier for the function call
 * @param functionName - Name of the function to execute (should be "manage_notes")
 * @param args - Function arguments containing action and relevant parameters
 * @returns Promise resolving to the function call response
 * @throws Error if the request fails or times out
 */
export async function executeNotesFunction(
  callId: string,
  functionName: string,
  args: NotesArguments
): Promise<NotesFunctionResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FUNCTION_CALL_TIMEOUT_MS);

  try {
    const request: NotesFunctionRequest = {
      call_id: callId,
      function_name: functionName,
      arguments: args,
    };

    console.log(
      '[Notes Client] → Sending function call:',
      functionName,
      'action:',
      args.action,
      'call_id:',
      callId
    );

    const response = await fetch(`${BACKEND_URL}/api/notes/function-call`, {
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

    const data: NotesFunctionResponse = await response.json();

    console.log(
      '[Notes Client] ← Function result received for call_id:',
      data.call_id,
      'success:',
      data.result.success
    );

    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error('[Notes Client] ✗ Function call timeout after', FUNCTION_CALL_TIMEOUT_MS, 'ms');
        throw new Error(`Function execution timeout after ${FUNCTION_CALL_TIMEOUT_MS / 1000} seconds`);
      }
      console.error('[Notes Client] ✗ Function call error:', error.message);
      throw error;
    }

    throw new Error('Unknown error during function call');
  }
}

/**
 * Format notes result for sending to OpenAI
 * Converts the function call result into a JSON string for OpenAI
 *
 * @param result - The function call result from backend
 * @returns JSON string formatted for OpenAI function output
 */
export function formatNotesResult(result: NotesFunctionResult): string {
  if (!result.success) {
    return JSON.stringify({
      error: result.error || 'Unknown error occurred',
    });
  }

  // For operations that return notes
  if (result.data && result.data.notes.length > 0) {
    return JSON.stringify({
      message: result.message,
      notes: result.data.notes,
      count: result.data.count,
    });
  }

  // For operations without note data (e.g., delete, empty list)
  return JSON.stringify({
    message: result.message,
    count: result.data?.count || 0,
  });
}
