import { z } from 'zod';
import { AgentType } from '../../types';

interface AgentCapabilities {
  documentGeneration: boolean;
  templateManagement: boolean;
  codeGeneration: boolean;
}

interface AgentPermissions {
  canAccessCases: boolean;
  canModifyDocuments: boolean;
  canManageTemplates: boolean;
}

export const DocumentationAgentConfig = {
  type: AgentType.DOCUMENTATION,
  model: 'deepseek-ai/DeepSeek-Coder-V2-Instruct',
  contextWindow: 128000,
  temperature: 0.3,
  capabilities: {
    documentGeneration: true,
    templateManagement: true,
    codeGeneration: true,
  } as AgentCapabilities,
  permissions: {
    canAccessCases: true,
    canModifyDocuments: true,
    canManageTemplates: true,
  } as AgentPermissions,
};

export const configSchema = z.object({
  DEEPSEEK_DOCS_API_KEY: z.string(),
  MODEL_NAME: z.string().default('deepseek-ai/DeepSeek-Coder-V2-Instruct'),
  CONTEXT_WINDOW: z.number().default(128000),
});
