import { z } from 'zod';
import { AgentType } from '../../types';

interface AgentCapabilities {
  legalAnalysis: boolean;
  precedentSearch: boolean;
  caseEvaluation: boolean;
}

interface AgentPermissions {
  canAccessCases: boolean;
  canModifyDocuments: boolean;
  canScheduleHearings: boolean;
}

export const LegalAnalystConfig = {
  type: AgentType.LEGAL_ANALYST,
  model: 'deepseek-ai/deepseek-R1',
  contextWindow: 128000,
  temperature: 0.7,
  capabilities: {
    legalAnalysis: true,
    precedentSearch: true,
    caseEvaluation: true,
  } as AgentCapabilities,
  permissions: {
    canAccessCases: true,
    canModifyDocuments: true,
    canScheduleHearings: false,
  } as AgentPermissions,
};

export const configSchema = z.object({
  DEEPSEEK_LEGAL_API_KEY: z.string(),
  MODEL_NAME: z.string().default('deepseek-ai/deepseek-R1'),
  CONTEXT_WINDOW: z.number().default(128000),
});
