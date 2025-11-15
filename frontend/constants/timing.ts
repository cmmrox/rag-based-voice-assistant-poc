/**
 * Timing constants for the voice assistant application
 * Centralized timing values for better maintainability and clarity
 */

/**
 * Delay before sending response.create event after function output
 * This ensures the function output is processed before requesting a new response
 */
export const FUNCTION_OUTPUT_DELAY_MS = 100;

/**
 * Timeout for function call execution
 * If a function call doesn't complete within this time, an error is sent
 */
export const FUNCTION_CALL_TIMEOUT_MS = 30000;

/**
 * Delay for event processing
 * Used to ensure proper sequencing of events
 */
export const EVENT_PROCESSING_DELAY_MS = 100;
