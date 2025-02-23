import re
from typing import Dict, Any, Callable, Awaitable

class CommandRouter:
    def __init__(self):
        self.commands: Dict[str, Callable[[str, Dict[str, Any]], Awaitable[None]]] = {}
    
    def command(self, pattern: str):
        """
        Decorator to register command handlers
        
        Args:
            pattern: Command pattern to match (e.g. 'help', 'caso \d+')
        """
        def decorator(func: Callable[[str, Dict[str, Any]], Awaitable[None]]):
            self.commands[pattern] = func
            return func
        return decorator
    
    async def handle_command(self, text: str, event: Dict[str, Any]) -> bool:
        """
        Route a command to its handler
        
        Args:
            text: Command text
            event: Full Slack event data
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        for pattern, handler in self.commands.items():
            match = re.match(f"^{pattern}$", text, re.IGNORECASE)
            if match:
                await handler(text, event)
                return True
        return False
