import { CustomModelConfig } from "@opencanvas/shared/types";
import { LegalAnalystConfig } from "../agents/legal/config";
import { DocumentationAgentConfig } from "../agents/docs/config";
import { SecretaryAgentConfig } from "../agents/admin/config";

export function adaptToOpenCanvasConfig(config: any): CustomModelConfig {
  return {
    provider: "deepseek",
    temperatureRange: {
      min: 0.1,
      max: 1.0,
      default: config.temperature || 0.7,
      current: config.temperature || 0.7,
    },
    maxTokens: {
      min: 1,
      max: config.contextWindow || 128000,
      default: config.contextWindow || 128000,
      current: config.contextWindow || 128000,
    },
  };
}

export const AGENT_CONFIGS = {
  legal: {
    name: LegalAnalystConfig.model,
    label: "Analista Legal",
    isLocked: true,
    config: adaptToOpenCanvasConfig(LegalAnalystConfig),
  },
  documentation: {
    name: DocumentationAgentConfig.model,
    label: "Documentación",
    isLocked: true,
    config: adaptToOpenCanvasConfig(DocumentationAgentConfig),
  },
  secretary: {
    name: SecretaryAgentConfig.model,
    label: "Secretario",
    isLocked: true,
    config: adaptToOpenCanvasConfig(SecretaryAgentConfig),
  },
};
