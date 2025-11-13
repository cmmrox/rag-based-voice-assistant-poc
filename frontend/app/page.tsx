'use client';

import { useState } from 'react';
import { useVoiceSession } from '@/hooks/useVoiceSession';
import MicrophoneButton from '@/components/MicrophoneButton';
import StatusIndicator from '@/components/StatusIndicator';
import Transcript from '@/components/Transcript';
import ErrorMessage from '@/components/ErrorMessage';

export default function Home() {
  const {
    status,
    transcript,
    error,
    startSession,
    stopSession,
    addTranscriptMessage
  } = useVoiceSession();

  const [dismissedError, setDismissedError] = useState<string | null>(null);

  const handleMicrophoneClick = async () => {
    if (status === 'idle' || status === 'error') {
      await startSession();
    } else {
      stopSession();
    }
  };

  const displayError = error && error !== dismissedError ? error : null;

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
            onDismiss={() => setDismissedError(error || null)}
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
