"""
AI Agents Module.
Contains implementations of different AI agents and their interactions.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize base agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        self.config = config
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Dict containing processing results
        """
        pass
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data before processing.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
