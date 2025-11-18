/**
 * Tool definitions for OpenAI Realtime API function calling
 * Defines the RAG knowledge base and notes management tool configurations
 */

export const RAG_KNOWLEDGE_TOOL = {
  type: 'function' as const,
  name: 'rag_knowledge',
  description:
    'Search and retrieve information from the knowledge base. Use this when the user asks questions that require specific information from documents or data sources.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The search query to find relevant information in the knowledge base',
      },
    },
    required: ['query'],
  },
};

export const NOTES_TOOL = {
  type: 'function' as const,
  name: 'manage_notes',
  description:
    'Create, retrieve, update, delete, or search notes from previous conversations. Use this when the user wants to save information for later, retrieve saved notes, or search through their notes.',
  parameters: {
    type: 'object',
    properties: {
      action: {
        type: 'string',
        enum: ['create', 'list', 'search', 'update', 'delete'],
        description: 'The action to perform on notes',
      },
      title: {
        type: 'string',
        description: 'Title of the note (required for create, optional for update)',
      },
      content: {
        type: 'string',
        description: 'Content of the note (required for create, optional for update)',
      },
      note_id: {
        type: 'string',
        description: 'ID of the note (required for update/delete, optional for list to get specific note)',
      },
      query: {
        type: 'string',
        description: 'Search query to find notes (required for search action)',
      },
    },
    required: ['action'],
  },
};
