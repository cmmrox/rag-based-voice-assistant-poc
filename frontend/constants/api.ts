/**
 * API configuration constants
 * Centralized API endpoints and configuration values
 */

/**
 * Base URL for the backend API
 * Falls back to localhost if not specified in environment
 */
export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8002';

/**
 * OpenAI Realtime API model identifier
 */
export const OPENAI_MODEL = 'gpt-4o-realtime-preview-2024-12-17';

/**
 * OpenAI Realtime API base URL
 */
export const OPENAI_REALTIME_URL = 'https://api.openai.com/v1/realtime';
