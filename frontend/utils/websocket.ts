/**
 * WebSocket utility functions
 * Helper functions for managing WebSocket connections to the backend
 */

/**
 * Generates WebSocket URL from HTTP/HTTPS backend URL
 *
 * @param backendUrl - The HTTP(S) backend URL
 * @param sessionId - The session ID to connect to
 * @returns WebSocket URL (ws:// or wss://)
 */
export function generateWebSocketUrl(backendUrl: string, sessionId: string): string {
  const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
  const wsUrl = backendUrl.replace(/^https?/, wsProtocol);
  return `${wsUrl}/api/ws/events/${sessionId}`;
}

/**
 * Sends a function call request to the backend via WebSocket
 *
 * @param websocket - The WebSocket connection
 * @param callId - The function call ID
 * @param functionName - The name of the function to call
 * @param args - The function arguments
 */
export function sendFunctionCallToBackend(
  websocket: WebSocket,
  callId: string,
  functionName: string,
  args: Record<string, any>
): void {
  if (websocket.readyState === WebSocket.OPEN) {
    websocket.send(
      JSON.stringify({
        type: 'function_call',
        call_id: callId,
        function_name: functionName,
        arguments: args,
      })
    );
    console.log('[RAG] → Sent function call to backend:', functionName, 'call_id:', callId);
  } else {
    console.error('[RAG] ✗ WebSocket not available for function call execution');
  }
}
