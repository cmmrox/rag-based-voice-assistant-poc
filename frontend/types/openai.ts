/**
 * TypeScript type definitions for OpenAI Realtime API events and responses
 * These types provide type safety for WebRTC data channel communication with OpenAI
 */

/**
 * Base interface for all OpenAI events
 */
export interface OpenAIEvent {
  type: string;
  event_id?: string;
  timestamp?: string;
  [key: string]: any;
}

/**
 * Function call event from OpenAI
 * Triggered when the model wants to call a function
 */
export interface FunctionCallEvent extends OpenAIEvent {
  type: 'response.function_call_arguments.done';
  call_id: string;
  name: string;
  arguments: string;
}

/**
 * Function call output event to send back to OpenAI
 */
export interface FunctionCallOutputEvent extends OpenAIEvent {
  type: 'conversation.item.create';
  item: {
    type: 'function_call_output';
    call_id: string;
    output: string;
  };
}

/**
 * Response create event to trigger model response
 */
export interface ResponseCreateEvent extends OpenAIEvent {
  type: 'response.create';
}

/**
 * Conversation item create event for sending messages
 */
export interface ConversationItemCreateEvent extends OpenAIEvent {
  type: 'conversation.item.create';
  item: {
    type: 'message';
    role: 'user' | 'assistant';
    content: Array<{
      type: 'input_text' | 'text';
      text: string;
    }>;
  };
}

/**
 * Session update event for configuring the session
 */
export interface SessionUpdateEvent extends OpenAIEvent {
  type: 'session.update';
  session: {
    modalities?: string[];
    instructions?: string;
    voice?: string;
    input_audio_format?: string;
    output_audio_format?: string;
    input_audio_transcription?: {
      model: string;
    };
    turn_detection?: {
      type: string;
      threshold?: number;
      prefix_padding_ms?: number;
      silence_duration_ms?: number;
    };
    tools?: Array<{
      type: string;
      name: string;
      description: string;
      parameters: any;
    }>;
    tool_choice?: string;
    temperature?: number;
    max_response_output_tokens?: number;
  };
}

/**
 * Response audio transcript event
 * Contains the transcription of the assistant's speech
 */
export interface ResponseAudioTranscriptEvent extends OpenAIEvent {
  type: 'response.audio_transcript.delta' | 'response.audio_transcript.done';
  transcript?: string;
  delta?: string;
}

/**
 * Conversation item input audio transcription event
 * Contains the transcription of the user's speech
 */
export interface InputAudioTranscriptionEvent extends OpenAIEvent {
  type: 'conversation.item.input_audio_transcription.completed';
  transcript: string;
}
