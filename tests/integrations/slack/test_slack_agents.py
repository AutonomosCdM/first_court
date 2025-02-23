import pytest
import asyncio
import re
import sys
import os
from unittest.mock import AsyncMock, patch

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from src.integrations.slack.agents.secretary_app import SecretarySlackApp
from src.integrations.slack.agents.judge_app import JudgeSlackApp
from src.integrations.slack.agents.prosecutor_app import ProsecutorSlackApp
from src.integrations.slack.agents.defender_app import DefenderSlackApp

class TestSlackAgents:
    @pytest.fixture
    async def secretary_agent(self):
        agent = SecretarySlackApp()
        await agent.initialize()
        return agent

    @pytest.fixture
    async def judge_agent(self):
        agent = JudgeSlackApp()
        await agent.initialize()
        return agent

    @pytest.fixture
    async def prosecutor_agent(self):
        agent = ProsecutorSlackApp()
        await agent.initialize()
        return agent

    @pytest.fixture
    async def defender_agent(self):
        agent = DefenderSlackApp()
        await agent.initialize()
        return agent

    @pytest.mark.asyncio
    async def test_secretary_case_creation(self, secretary_agent):
        """Test creating a new case"""
        mock_event = {
            "channel": "test-channel",
            "text": "caso nuevo \"Demanda por incumplimiento de contrato\"",
            "ts": "1234567890.000000"
        }
        
        # Mock the notifier to capture case updates
        secretary_agent.notifier.send_case_update = AsyncMock()
        secretary_agent.notifier.send_notification = AsyncMock()
        
        # Handle the message
        await secretary_agent.handle_message(mock_event)
        
        # Assert case update was sent
        secretary_agent.notifier.send_case_update.assert_called_once()
        secretary_agent.notifier.send_notification.assert_called_once()
        
        # Verify case details
        case_update_args = secretary_agent.notifier.send_case_update.call_args[1]
        assert case_update_args['update_type'] == 'Caso Creado'
        assert 'Demanda por incumplimiento de contrato' in case_update_args['description']

    @pytest.mark.asyncio
    async def test_judge_resolution(self, judge_agent):
        """Test judge issuing a resolution"""
        mock_event = {
            "channel": "test-channel",
            "text": "resolver 2025-001 providencia \"Traslado a la parte demandada\"",
            "ts": "1234567890.000000"
        }
        
        # Mock the notifier to capture case updates
        judge_agent.notifier.send_case_update = AsyncMock()
        judge_agent.add_reaction = AsyncMock()
        
        # Handle the message
        await judge_agent.handle_message(mock_event)
        
        # Assert case update was sent
        judge_agent.notifier.send_case_update.assert_called_once()
        judge_agent.add_reaction.assert_called_once()
        
        # Verify resolution details
        case_update_args = judge_agent.notifier.send_case_update.call_args[1]
        assert case_update_args['case_number'] == '2025-001'
        assert case_update_args['update_type'] == 'Nueva Resolución: providencia'
        assert 'Traslado a la parte demandada' in case_update_args['description']

    @pytest.mark.asyncio
    async def test_prosecutor_accusation(self, prosecutor_agent):
        """Test prosecutor presenting an accusation"""
        mock_event = {
            "channel": "test-channel",
            "text": "acusar 2025-001 \"Incumplimiento de contrato\"",
            "ts": "1234567890.000000"
        }
        
        # Mock the notifier to capture case updates
        prosecutor_agent.notifier.send_case_update = AsyncMock()
        prosecutor_agent.add_reaction = AsyncMock()
        
        # Handle the message
        await prosecutor_agent.handle_message(mock_event)
        
        # Assert case update was sent
        prosecutor_agent.notifier.send_case_update.assert_called_once()
        prosecutor_agent.add_reaction.assert_called_once()
        
        # Verify accusation details
        case_update_args = prosecutor_agent.notifier.send_case_update.call_args[1]
        assert case_update_args['case_number'] == '2025-001'
        assert case_update_args['update_type'] == 'Nueva Acusación'
        assert 'Incumplimiento de contrato' in case_update_args['description']

    @pytest.mark.asyncio
    async def test_defender_defense(self, defender_agent):
        """Test defender presenting a defense"""
        mock_event = {
            "channel": "test-channel",
            "text": "defender 2025-001 \"Cumplimiento efectivo del contrato\"",
            "ts": "1234567890.000000"
        }
        
        # Mock the notifier to capture case updates
        defender_agent.notifier.send_case_update = AsyncMock()
        defender_agent.add_reaction = AsyncMock()
        
        # Handle the message
        await defender_agent.handle_message(mock_event)
        
        # Assert case update was sent
        defender_agent.notifier.send_case_update.assert_called_once()
        defender_agent.add_reaction.assert_called_once()
        
        # Verify defense details
        case_update_args = defender_agent.notifier.send_case_update.call_args[1]
        assert case_update_args['case_number'] == '2025-001'
        assert case_update_args['update_type'] == 'Nueva Defensa'
        assert 'Cumplimiento efectivo del contrato' in case_update_args['description']

    @pytest.mark.asyncio
    async def test_command_router_regex_patterns(self):
        """Test regex patterns for command matching"""
        test_cases = [
            # Secretary
            (r"caso nuevo (.*)", "caso nuevo Demanda por incumplimiento", True),
            (r"caso (\d{4}-\d{3})", "caso 2025-001", True),
            (r"audiencia (\d{4}-\d{2}-\d{2}) (\d{4}-\d{3})", "audiencia 2024-03-01 2025-001", True),
            
            # Judge
            (r"resolver (\d{4}-\d{3}) (\w+) \"(.+)\"", "resolver 2025-001 providencia \"Traslado a la parte demandada\"", True),
            (r"fallo (\d{4}-\d{3}) \"(.+)\"", "fallo 2025-001 \"Se acoge la demanda\"", True),
            (r"admitir (\d{4}-\d{3})", "admitir 2025-001", True),
            
            # Prosecutor
            (r"acusar (\d{4}-\d{3}) \"(.+)\"", "acusar 2025-001 \"Incumplimiento de contrato\"", True),
            (r"prueba (\d{4}-\d{3}) (\w+) \"(.+)\"", "prueba 2025-001 documental \"Contrato firmado\"", True),
            (r"investigar (\d{4}-\d{3}) \"(.+)\"", "investigar 2025-001 \"Análisis de documentación\"", True),
            
            # Defender
            (r"defender (\d{4}-\d{3}) \"(.+)\"", "defender 2025-001 \"Cumplimiento efectivo del contrato\"", True),
            (r"recurso (\d{4}-\d{3}) (\w+) \"(.+)\"", "recurso 2025-001 apelación \"Errónea valoración de la prueba\"", True),
            (r"alegar (\d{4}-\d{3}) \"(.+)\"", "alegar 2025-001 \"La parte demandante no ha probado el incumplimiento\"", True),
        ]
        
        for pattern, text, expected in test_cases:
            match = re.match(pattern, text)
            assert match is not None, f"Failed to match pattern: {pattern} with text: {text}"

    @pytest.mark.asyncio
    async def test_help_command(self, secretary_agent, judge_agent, prosecutor_agent, defender_agent):
        """Test help command for each agent"""
        help_events = [
            {"channel": "test-channel", "text": "ayuda", "ts": "1234567890.000000"},
        ]
        
        agents = [secretary_agent, judge_agent, prosecutor_agent, defender_agent]
        
        for agent in agents:
            # Mock send_message to capture help text
            agent.send_message = AsyncMock()
            
            # Handle help command
            await agent.handle_message(help_events[0])
            
            # Assert help message was sent
            agent.send_message.assert_called_once()
            
            # Verify help text contains expected keywords
            help_text = agent.send_message.call_args[1]['text']
            assert len(help_text) > 100, "Help text seems too short"
            assert "Comandos" in help_text, "Help text should list available commands"
