'use client';

import { SessionStatus } from '@/types/session';

/**
 * Props for the MicrophoneButton component
 */
interface MicrophoneButtonProps {
  /** Whether the microphone is currently listening */
  isListening: boolean;
  /** Current session status */
  status: SessionStatus;
  /** Click handler for the button */
  onClick: () => void;
}

/**
 * Button configuration object
 * Maps each session status to its display text and styling
 */
const BUTTON_CONFIG: Record<
  SessionStatus,
  {
    text: string;
    baseClasses: string;
    colorClasses: string;
    showSpinner: boolean;
  }
> = {
  idle: {
    text: 'Start Voice',
    baseClasses: 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]',
    colorClasses: 'bg-blue-500 hover:bg-blue-600',
    showSpinner: false,
  },
  connecting: {
    text: 'Connecting...',
    baseClasses: 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]',
    colorClasses: 'bg-yellow-500 hover:bg-yellow-600',
    showSpinner: false,
  },
  listening: {
    text: 'Listening...',
    baseClasses: 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]',
    colorClasses: 'bg-green-500 hover:bg-green-600 animate-pulse',
    showSpinner: false,
  },
  processing: {
    text: 'Processing...',
    baseClasses: 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]',
    colorClasses: 'bg-yellow-500 hover:bg-yellow-600',
    showSpinner: true,
  },
  speaking: {
    text: 'Speaking...',
    baseClasses: 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]',
    colorClasses: 'bg-blue-500 hover:bg-blue-600',
    showSpinner: false,
  },
  error: {
    text: 'Error',
    baseClasses: 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]',
    colorClasses: 'bg-red-500 hover:bg-red-600',
    showSpinner: false,
  },
};

/**
 * Loading spinner SVG component
 */
function LoadingSpinner() {
  return (
    <span className="inline-block mr-2">
      <svg
        className="animate-spin h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </span>
  );
}

/**
 * MicrophoneButton Component
 *
 * Interactive button for controlling voice session.
 * Changes appearance and text based on the current session status.
 * Shows a loading spinner during processing state.
 *
 * @param isListening - Whether the microphone is currently active
 * @param status - Current session status
 * @param onClick - Handler function called when button is clicked
 */
export default function MicrophoneButton({ isListening, status, onClick }: MicrophoneButtonProps) {
  const config = BUTTON_CONFIG[status] || BUTTON_CONFIG.idle;
  const isDisabled = status === 'processing';

  return (
    <button
      onClick={onClick}
      className={`${config.baseClasses} ${config.colorClasses}`}
      disabled={isDisabled}
    >
      {config.showSpinner && <LoadingSpinner />}
      {config.text}
    </button>
  );
}

