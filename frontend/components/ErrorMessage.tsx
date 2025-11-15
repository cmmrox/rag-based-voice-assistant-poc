'use client';

/**
 * Props for the ErrorMessage component
 */
interface ErrorMessageProps {
  /** Error message to display, or null to hide the component */
  error: string | null;
  /** Optional callback function when user dismisses the error */
  onDismiss?: () => void;
}

/**
 * Error icon SVG component
 */
function ErrorIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
        clipRule="evenodd"
      />
    </svg>
  );
}

/**
 * Close button icon SVG component
 */
function CloseIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
        clipRule="evenodd"
      />
    </svg>
  );
}

/**
 * ErrorMessage Component
 *
 * Displays error messages to the user in a dismissible alert box.
 * Automatically hides when error is null.
 *
 * Features:
 * - Red styling to indicate error state
 * - Error icon for visual clarity
 * - Optional dismiss button
 * - Conditional rendering (returns null if no error)
 *
 * Usage:
 * ```tsx
 * <ErrorMessage
 *   error="Connection failed"
 *   onDismiss={() => setError(null)}
 * />
 * ```
 *
 * @param error - The error message to display, or null to hide
 * @param onDismiss - Optional callback when user clicks the dismiss button
 * @returns Error alert component or null if no error
 */
export default function ErrorMessage({ error, onDismiss }: ErrorMessageProps) {
  if (!error) {
    return null;
  }

  return (
    <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <ErrorIcon />
        <span>{error}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-600 hover:text-red-800 ml-4"
          aria-label="Dismiss error"
        >
          <CloseIcon />
        </button>
      )}
    </div>
  );
}

