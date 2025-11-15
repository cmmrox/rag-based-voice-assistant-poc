/**
 * TypeScript type definitions for voice session management
 * Defines the session status and transcript message types
 */

/**
 * Session status enumeration
 * Represents the current state of the voice assistant session
 */
export type SessionStatus =
  | 'idle'          // No active session
  | 'connecting'    // Establishing connection to OpenAI
  | 'listening'     // Actively listening for user input
  | 'processing'    // Processing user input or function calls
  | 'speaking'      // Assistant is speaking
  | 'error';        // Error state

/**
 * Transcript message type
 * Represents a single message in the conversation transcript
 */
export interface TranscriptMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}
