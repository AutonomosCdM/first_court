import { AgentType, AgentAction } from '../../types';

type AgentActionMap = {
  [key in AgentType]: {
    [key: string]: AgentAction;
  };
};

export const AgentActions: AgentActionMap = {
  [AgentType.LEGAL_ANALYST]: {
    ANALYZE_CASE: {
      name: 'analyze_case',
      description: 'Analizar un caso legal completo',
      requiresVerification: true,
      model: 'deepseek-ai/deepseek-R1',
    },
    GENERATE_SUMMARY: {
      name: 'generate_summary',
      description: 'Generar resumen de caso',
      requiresVerification: false,
      model: 'deepseek-ai/deepseek-R1',
    },
  },
  [AgentType.DOCUMENTATION]: {
    CREATE_DOCUMENT: {
      name: 'create_document',
      description: 'Crear nuevo documento legal',
      requiresTemplate: true,
      model: 'deepseek-ai/DeepSeek-Coder-V2-Instruct',
    },
    MODIFY_TEMPLATE: {
      name: 'modify_template',
      description: 'Modificar plantilla existente',
      requiresApproval: true,
      model: 'deepseek-ai/DeepSeek-Coder-V2-Instruct',
    },
  },
  [AgentType.SECRETARY]: {
    SCHEDULE_HEARING: {
      name: 'schedule_hearing',
      description: 'Agendar audiencia',
      requiresCalendarCheck: true,
      model: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
    },
    SEND_NOTIFICATION: {
      name: 'send_notification',
      description: 'Enviar notificación',
      requiresTemplate: true,
      model: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
    },
  },
};
