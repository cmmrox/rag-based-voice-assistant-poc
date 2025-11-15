'use client';

import { SessionStatus } from '@/types/session';

/**
 * Props for the StatusIndicator component
 */
interface StatusIndicatorProps {
  status: SessionStatus;
}

/**
 * Status configuration object
 * Maps each session status to its display text and color
 */
const STATUS_CONFIG: Record<
  SessionStatus,
  {
    text: string;
    textColor: string;
    bgColor: string;
  }
> = {
  idle: {
    text: 'Idle',
    textColor: 'text-gray-500',
    bgColor: 'bg-gray-500',
  },
  connecting: {
    text: 'Connecting...',
    textColor: 'text-yellow-500',
    bgColor: 'bg-yellow-500',
  },
  listening: {
    text: 'Listening',
    textColor: 'text-green-600',
    bgColor: 'bg-green-600',
  },
  processing: {
    text: 'Processing',
    textColor: 'text-yellow-600',
    bgColor: 'bg-yellow-600',
  },
  speaking: {
    text: 'Speaking',
    textColor: 'text-blue-600',
    bgColor: 'bg-blue-600',
  },
  error: {
    text: 'Error',
    textColor: 'text-red-600',
    bgColor: 'bg-red-600',
  },
};

/**
 * StatusIndicator Component
 *
 * Displays the current session status with a colored indicator dot and text label.
 * The color changes based on the current status to provide visual feedback to the user.
 *
 * @param status - The current session status
 */
export default function StatusIndicator({ status }: StatusIndicatorProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.idle;

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${config.bgColor}`}></div>
      <span className={`text-sm font-medium ${config.textColor}`}>
        Status: {config.text}
      </span>
    </div>
  );
}

