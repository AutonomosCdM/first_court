// Tipos de agentes
export enum AgentType {
  LEGAL_ANALYST = 'legal_analyst',
  DOCUMENTATION = 'documentation',
  SECRETARY = 'secretary',
}

// Interfaces base para agentes
export interface BaseAgentConfig {
  type: AgentType;
  model: string;
  contextWindow: number;
  temperature: number;
}

// Interfaces para acciones
export interface AgentAction {
  name: string;
  description: string;
  model: string;
  requiresVerification?: boolean;
  requiresTemplate?: boolean;
  requiresApproval?: boolean;
  requiresCalendarCheck?: boolean;
}

// Interfaces para capacidades y permisos
export interface BaseCapabilities {
  [key: string]: boolean;
}

export interface BasePermissions {
  canAccessCases: boolean;
  [key: string]: boolean;
}

// Tipos para configuración de Google
export interface GoogleConfig {
  scopes: Record<string, string[]>;
  paths: Record<string, string>;
  documentTypes: Record<string, string>;
}
