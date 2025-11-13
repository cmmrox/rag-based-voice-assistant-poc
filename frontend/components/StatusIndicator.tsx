'use client';

import { SessionStatus } from '@/hooks/useVoiceSession';

interface StatusIndicatorProps {
  status: SessionStatus;
}

export default function StatusIndicator({ status }: StatusIndicatorProps) {
  const getStatusText = () => {
    switch (status) {
      case 'idle':
        return 'Idle';
      case 'connecting':
        return 'Connecting...';
      case 'connected':
        return 'Ready';
      case 'listening':
        return 'Listening';
      case 'processing':
        return 'Processing';
      case 'speaking':
        return 'Speaking';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'idle':
        return 'text-gray-500';
      case 'connecting':
        return 'text-yellow-500';
      case 'connected':
        return 'text-green-500';
      case 'listening':
        return 'text-green-600';
      case 'processing':
        return 'text-yellow-600';
      case 'speaking':
        return 'text-blue-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${getStatusColor().replace('text-', 'bg-')}`}></div>
      <span className={`text-sm font-medium ${getStatusColor()}`}>
        Status: {getStatusText()}
      </span>
    </div>
  );
}

