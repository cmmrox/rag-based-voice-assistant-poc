'use client';

import { SessionStatus } from '@/hooks/useVoiceSession';

interface MicrophoneButtonProps {
  isListening: boolean;
  status: SessionStatus;
  onClick: () => void;
}

export default function MicrophoneButton({ isListening, status, onClick }: MicrophoneButtonProps) {
  const getButtonText = () => {
    switch (status) {
      case 'listening':
        return 'Listening...';
      case 'processing':
        return 'Processing...';
      case 'speaking':
        return 'Speaking...';
      case 'error':
        return 'Error';
      case 'connected':
        return 'Stop';
      default:
        return 'Start Voice';
    }
  };

  const getButtonClass = () => {
    const baseClass = 'px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 min-w-[140px]';
    
    switch (status) {
      case 'listening':
        return `${baseClass} bg-green-500 hover:bg-green-600 animate-pulse`;
      case 'processing':
        return `${baseClass} bg-yellow-500 hover:bg-yellow-600`;
      case 'speaking':
        return `${baseClass} bg-blue-500 hover:bg-blue-600`;
      case 'error':
        return `${baseClass} bg-red-500 hover:bg-red-600`;
      case 'connected':
        return `${baseClass} bg-red-500 hover:bg-red-600`;
      default:
        return `${baseClass} bg-blue-500 hover:bg-blue-600`;
    }
  };

  return (
    <button
      onClick={onClick}
      className={getButtonClass()}
      disabled={status === 'processing'}
    >
      {status === 'processing' && (
        <span className="inline-block mr-2">
          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
      )}
      {getButtonText()}
    </button>
  );
}

