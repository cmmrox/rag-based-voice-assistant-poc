/**
 * Tool definitions for OpenAI Realtime API function calling
 * Defines the RAG knowledge base tool configuration
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
