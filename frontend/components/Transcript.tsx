'use client';

import { memo, useEffect, useRef } from 'react';
import { TranscriptMessage } from '@/types/session';

/**
 * Props for the Transcript component
 */
interface TranscriptProps {
  /** Array of transcript messages to display */
  messages: TranscriptMessage[];
}

/**
 * Individual message component (memoized for performance)
 */
const MessageBubble = memo(function MessageBubble({ message }: { message: TranscriptMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-white text-gray-800 border border-gray-200'
        }`}
      >
        <div className="text-xs opacity-70 mb-1">
          {isUser ? 'You' : 'Assistant'}
        </div>
        <div className="whitespace-pre-wrap break-words">{message.text}</div>
      </div>
    </div>
  );
});

/**
 * Transcript Component
 *
 * Displays a chat-like transcript of the conversation between user and assistant.
 * Messages are shown in chronological order with automatic scrolling to the latest message.
 * User messages appear on the right in blue, assistant messages on the left in white.
 *
 * Features:
 * - Auto-scroll to newest messages
 * - Empty state when no messages exist
 * - Memoized message bubbles for optimal performance
 * - Responsive message bubbles with text wrapping
 *
 * @param messages - Array of transcript messages to display
 */
const Transcript = memo(function Transcript({ messages }: TranscriptProps) {
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
        <MessageBubble key={`${message.timestamp}-${index}`} message={message} />
      ))}
      <div ref={transcriptEndRef} />
    </div>
  );
});

export default Transcript;

