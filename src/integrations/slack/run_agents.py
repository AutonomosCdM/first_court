import asyncio
import signal
from typing import List, Dict, Any
import sys
import os

# Ensure the project root is in the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from integrations.slack.agents.secretary_app import SecretarySlackApp
from integrations.slack.agents.judge_app import JudgeSlackApp
from integrations.slack.agents.prosecutor_app import ProsecutorSlackApp
from integrations.slack.agents.defender_app import DefenderSlackApp

class CourtAgentsRunner:
    def __init__(self):
        self.agents = [
            SecretarySlackApp(),
            JudgeSlackApp(),
            ProsecutorSlackApp(),
            DefenderSlackApp()
        ]
        self.running = True
        
    async def start_agents(self):
        """Start all court agents"""
        try:
            # Register signal handlers
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, self.handle_shutdown)
            
            print("🏛️  Iniciando Sistema Judicial...")
            
            # Start all agents concurrently
            tasks = []
            for agent in self.agents:
                task = asyncio.create_task(agent.start())
                tasks.append(task)
            
            print("✅ Todos los agentes están en línea!")
            print("\nAgentes activos:")
            print("• 👨‍⚖️ Juez")
            print("• 👨‍💼 Secretario")
            print("• 👨‍⚖️ Fiscal")
            print("• 👨‍💼 Defensor")
            print("\nPresiona Ctrl+C para detener el sistema")
            
            # Wait for all agents
            await asyncio.gather(*tasks)
            
        except Exception as e:
            print(f"\n❌ Error iniciando agentes: {e}")
            await self.shutdown()
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        if self.running:
            print("\n🛑 Recibida señal de apagado...")
            self.running = False
            asyncio.create_task(self.shutdown())
    
    async def shutdown(self):
        """Shutdown all agents gracefully"""
        print("🔄 Apagando agentes...")
        
        for agent in self.agents:
            try:
                await agent.cleanup()
            except Exception as e:
                print(f"❌ Error apagando agente {agent.__class__.__name__}: {e}")
        
        print("👋 Sistema apagado correctamente")
        sys.exit(0)

async def main():
    runner = CourtAgentsRunner()
    await runner.start_agents()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Apagando sistema...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
