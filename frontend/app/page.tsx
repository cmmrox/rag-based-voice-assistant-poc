'use client';

import { useState } from 'react';
import { useVoiceSession } from '@/hooks/useVoiceSession';
import MicrophoneButton from '@/components/MicrophoneButton';
import StatusIndicator from '@/components/StatusIndicator';
import Transcript from '@/components/Transcript';
import ErrorMessage from '@/components/ErrorMessage';

/**
 * Home Page Component
 *
 * Main application page for the RAG-based voice assistant.
 * Manages the voice session lifecycle and displays the conversation interface.
 *
 * Features:
 * - Voice session control (start/stop)
 * - Real-time conversation transcript
 * - Session status indicator
 * - Error message display with dismissal
 */
export default function Home() {
  const {
    status,
    transcript,
    error,
    startSession,
    stopSession,
  } = useVoiceSession();

  // Track which error was last dismissed to avoid showing the same error twice
  const [lastDismissedError, setLastDismissedError] = useState<string | null>(null);

  /**
   * Handles microphone button clicks
   * Starts a new session if idle or in error state, otherwise stops the current session
   */
  const handleMicrophoneClick = async () => {
    if (status === 'idle' || status === 'error') {
      await startSession();
    } else {
      stopSession();
    }
  };

  /**
   * Determines which error to display
   * Only shows errors that haven't been dismissed
   */
  const displayError = error && error !== lastDismissedError ? error : null;

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-100">
      <div className="w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          Voice Assistant POC
        </h1>

        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Error Message */}
          <ErrorMessage
            error={displayError}
            onDismiss={() => setLastDismissedError(error || null)}
          />

          {/* Microphone Button and Status */}
          <div className="flex flex-col items-center gap-4 mb-8">
            <MicrophoneButton
              isListening={status !== 'idle'}
              status={status}
              onClick={handleMicrophoneClick}
            />
            <StatusIndicator status={status} />
          </div>

          {/* Transcript */}
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-2 text-gray-700">Conversation</h2>
            <Transcript messages={transcript} />
          </div>
        </div>

        <div className="mt-4 text-center text-sm text-gray-500">
          <p>RAG-based Voice Assistant - Proof of Concept</p>
        </div>
      </div>
    </main>
  );
}
