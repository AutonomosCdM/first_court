"""
Message Formatter for structuring messages in a consistent manner.
"""

from typing import Dict, Any, List

class MessageFormatter:
    @staticmethod
    def format_agent_message(agent_name: str, role: str, message: str) -> str:
        """
        Format a message from an agent with consistent styling.
        
        Args:
            agent_name (str): Name of the agent
            role (str): Role of the agent
            message (str): Content of the message
        
        Returns:
            str: Formatted message
        """
        return f"*{agent_name}* ({role}):\n{message}"

    @staticmethod
    def format_case_summary(case_summary: Dict[str, Any]) -> str:
        """
        Format a case summary for Slack message.
        
        Args:
            case_summary (dict): Dictionary containing case details
        
        Returns:
            str: Formatted case summary
        """
        return f"""
*Resumen de Caso*
• Tipo de Caso: {case_summary.get('case_type', 'No especificado')}
• Palabras Clave: {case_summary.get('keywords', 'Sin palabras clave')}
• Puntos de Reacción Rápida: {case_summary.get('quick_reaction_points', 'Sin puntos identificados')}
• Direcciones de Respuesta: {case_summary.get('response_directions', 'Sin direcciones específicas')}
"""

    @staticmethod
    def format_legal_reflection(legal_reflection: Dict[str, Any]) -> str:
        """
        Format legal reflection for Slack message.
        
        Args:
            legal_reflection (dict): Dictionary containing legal reflection details
        
        Returns:
            str: Formatted legal reflection
        """
        if not legal_reflection.get('needed_reference', False):
            return "No se requirieron referencias legales adicionales."
        
        laws = legal_reflection.get('laws', [])
        formatted_laws = "\n".join([
            f"- *{law.get('metadata', {}).get('lawName', 'Ley no identificada')}*: "
            f"{law.get('content', 'Sin detalles')}"
            for law in laws
        ])
        
        return f"""
*Reflexión Legal*
• Consulta: {legal_reflection.get('query', 'Sin consulta específica')}
• Leyes Relevantes:
{formatted_laws}
"""

    @staticmethod
    def create_slack_blocks_for_case(case_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create Slack message blocks for a case summary.
        
        Args:
            case_summary (dict): Dictionary containing case details
        
        Returns:
            List of Slack block kit blocks
        """
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Nuevo Caso Judicial*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Tipo de Caso:*\n{case_summary.get('case_type', 'No especificado')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Palabras Clave:*\n{case_summary.get('keywords', 'Sin palabras clave')}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Puntos de Reacción Rápida:* {case_summary.get('quick_reaction_points', 'Sin puntos identificados')}"
                    }
                ]
            }
        ]
