'use client';

import { useEffect, useRef } from 'react';
import { TranscriptMessage } from '@/hooks/useVoiceSession';

interface TranscriptProps {
  messages: TranscriptMessage[];
}

export default function Transcript({ messages }: TranscriptProps) {
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <p>No messages yet. Start a voice session to begin.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 h-96 overflow-y-auto p-4 bg-gray-50 rounded-lg">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-2 ${
              message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-800 border border-gray-200'
            }`}
          >
            <div className="text-xs opacity-70 mb-1">
              {message.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div className="whitespace-pre-wrap break-words">{message.text}</div>
          </div>
        </div>
      ))}
      <div ref={transcriptEndRef} />
    </div>
  );
}

