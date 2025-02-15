import { CustomModelConfig } from "@opencanvas/shared/types";

export type AgentType = "legal" | "documentation" | "secretary";

export interface AgentCapabilities {
  canAnalyzeLegal: boolean;
  canGenerateDocuments: boolean;
  canManageCalendar: boolean;
  canSendEmails: boolean;
  canReflect: boolean;
  canVerify: boolean;
}

export interface AgentConfiguration extends CustomModelConfig {
  type: AgentType;
  capabilities: AgentCapabilities;
  apiKey?: string;
  baseUrl?: string;
}

export const DEFAULT_CAPABILITIES: Record<AgentType, AgentCapabilities> = {
  legal: {
    canAnalyzeLegal: true,
    canGenerateDocuments: true,
    canManageCalendar: false,
    canSendEmails: false,
    canReflect: true,
    canVerify: true,
  },
  documentation: {
    canAnalyzeLegal: false,
    canGenerateDocuments: true,
    canManageCalendar: false,
    canSendEmails: false,
    canReflect: false,
    canVerify: true,
  },
  secretary: {
    canAnalyzeLegal: false,
    canGenerateDocuments: true,
    canManageCalendar: true,
    canSendEmails: true,
    canReflect: false,
    canVerify: false,
  },
};
