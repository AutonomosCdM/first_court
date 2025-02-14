import { z } from 'zod';
import { AgentType } from '../../types';

interface AgentCapabilities {
  calendarManagement: boolean;
  emailNotifications: boolean;
  formManagement: boolean;
}

interface AgentPermissions {
  canAccessCases: boolean;
  canScheduleHearings: boolean;
  canManageCalendar: boolean;
  canSendNotifications: boolean;
}

export const SecretaryAgentConfig = {
  type: AgentType.SECRETARY,
  model: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
  contextWindow: 32000,
  temperature: 0.5,
  capabilities: {
    calendarManagement: true,
    emailNotifications: true,
    formManagement: true,
  } as AgentCapabilities,
  permissions: {
    canAccessCases: true,
    canScheduleHearings: true,
    canManageCalendar: true,
    canSendNotifications: true,
  } as AgentPermissions,
};

export const configSchema = z.object({
  DEEPSEEK_ADMIN_API_KEY: z.string(),
  MODEL_NAME: z.string().default('deepseek-ai/DeepSeek-R1-Distill-Qwen-32B'),
  CONTEXT_WINDOW: z.number().default(32000),
});
