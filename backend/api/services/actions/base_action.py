"""
Base Action Class
Abstract base class for all voice agent actions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from api.models.company import Company, CompanyIntent, Appointment
from api.core.database import get_session

logger = logging.getLogger(__name__)

class BaseAction(ABC):
    """
    Abstract base class for voice agent actions
    """
    
    def __init__(self, company: Company, intent: CompanyIntent):
        self.company = company
        self.intent = intent
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def validate_parameters(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize extracted entities
        Returns validated parameters or raises ValidationError
        """
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the action with validated parameters
        Returns result dictionary
        """
        pass
    
    @abstractmethod
    async def generate_response(self, result: Dict[str, Any]) -> str:
        """
        Generate voice response based on execution result
        """
        pass
    
    async def handle(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main handler - validates, executes, and generates response
        """
        try:
            # Validate parameters
            parameters = await self.validate_parameters(entities)
            
            # Check if confirmation is required
            if self.intent.requires_confirmation and not entities.get("confirmed"):
                return {
                    "status": "confirmation_required",
                    "parameters": parameters,
                    "response": await self.generate_confirmation_request(parameters)
                }
            
            # Execute action
            result = await self.execute(parameters)
            
            # Generate response
            response = await self.generate_response(result)
            
            return {
                "status": "success",
                "result": result,
                "response": response
            }
            
        except ValidationError as e:
            return {
                "status": "validation_error",
                "error": str(e),
                "response": await self.generate_validation_error_response(str(e))
            }
        except Exception as e:
            self.logger.error(f"Action execution error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "response": await self.generate_error_response()
            }
    
    async def generate_confirmation_request(self, parameters: Dict[str, Any]) -> str:
        """
        Generate confirmation request message
        """
        return "Let me confirm those details with you."
    
    async def generate_validation_error_response(self, error: str) -> str:
        """
        Generate response for validation errors
        """
        return f"I need some more information. {error}"
    
    async def generate_error_response(self) -> str:
        """
        Generate generic error response
        """
        return "I'm sorry, I encountered an issue processing your request. Please try again."
    
    def format_datetime(self, dt: datetime) -> str:
        """
        Format datetime for voice response
        """
        return dt.strftime("%A, %B %d at %I:%M %p")
    
    def format_date(self, dt: datetime) -> str:
        """
        Format date for voice response
        """
        return dt.strftime("%A, %B %d")
    
    def format_time(self, dt: datetime) -> str:
        """
        Format time for voice response
        """
        return dt.strftime("%I:%M %p")

class ValidationError(Exception):
    """
    Raised when parameter validation fails
    """
    pass