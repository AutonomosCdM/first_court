import os
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import quote

class GatherIntegrationError(Exception):
    """Custom exception for Gather API integration errors"""
    pass

class GatherIntegration:
    """
    Integration class for interacting with Gather.town HTTP API

    Attributes:
        _api_key (str): API key for authentication
        _base_url (str): Base URL for Gather API
        _logger (logging.Logger): Logger for tracking API interactions
    """

    def __init__(self, api_key: str):
        """
        Initialize Gather integration with API key

        Args:
            api_key (str): Gather API key for authentication
        """
        self._api_key = api_key
        self._base_url = "https://api.gather.town/api"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - Gather Integration - %(levelname)s: %(message)s'
        )
        self._logger = logging.getLogger(__name__)

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to Gather API

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Optional[Dict]): URL parameters
            data (Optional[Dict]): Request body data

        Returns:
            Dict[str, Any]: API response
        """
        url = f"{self._base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "apiKey": self._api_key
        }

        try:
            response = requests.request(
                method, 
                url, 
                headers=headers, 
                params=params, 
                json=data
            )
            response.raise_for_status()
            
            return response.json() if response.content else {}
        
        except requests.exceptions.RequestException as e:
            self._logger.error(f"API Request Error: {e}")
            raise GatherIntegrationError(f"API Request Failed: {e}")

    def create_space(
        self, 
        name: str, 
        source_space: str, 
        reason: Optional[str] = None
    ) -> str:
        """
        Create a new Gather space by copying an existing space

        Args:
            name (str): Name of the new space
            source_space (str): SpaceId of the template space to copy
            reason (Optional[str]): Reason for space creation

        Returns:
            str: SpaceId of the newly created space
        """
        endpoint = "/v2/spaces"
        payload = {
            "name": name,
            "sourceSpace": source_space
        }
        
        if reason:
            payload["reason"] = reason

        try:
            result = self._make_request("POST", endpoint, data=payload)
            return result
        except GatherIntegrationError as e:
            self._logger.error(f"Space Creation Error: {e}")
            raise

    def get_map(self, space_id: str, map_id: str) -> Dict[str, Any]:
        """
        Retrieve map data for a specific space and map

        Args:
            space_id (str): ID of the space
            map_id (str): ID of the map within the space

        Returns:
            Dict[str, Any]: Map data
        """
        # Replace forward slashes with backslashes for proper encoding
        encoded_space_id = quote(space_id.replace('/', '\\'))
        encoded_map_id = quote(map_id)
        
        endpoint = f"/v2/spaces/{encoded_space_id}/maps/{encoded_map_id}"

        try:
            return self._make_request("GET", endpoint)
        except GatherIntegrationError as e:
            self._logger.error(f"Map Retrieval Error: {e}")
            raise

    def set_map(
        self, 
        space_id: str, 
        map_id: str, 
        content: Dict[str, Any]
    ) -> None:
        """
        Set map contents for a specific space and map

        Args:
            space_id (str): ID of the space
            map_id (str): ID of the map within the space
            content (Dict[str, Any]): Map content to set
        """
        # Replace forward slashes with backslashes for proper encoding
        encoded_space_id = quote(space_id.replace('/', '\\'))
        encoded_map_id = quote(map_id)
        
        endpoint = f"/v2/spaces/{encoded_space_id}/maps/{encoded_map_id}"

        try:
            self._make_request("POST", endpoint, data={"content": content})
        except GatherIntegrationError as e:
            self._logger.error(f"Map Update Error: {e}")
            raise

    def get_email_guestlist(self, space_id: str) -> Dict[str, Any]:
        """
        Retrieve email guestlist for a space

        Args:
            space_id (str): ID of the space

        Returns:
            Dict[str, Any]: Guestlist keyed by email addresses
        """
        endpoint = "/getEmailGuestlist"
        params = {"spaceId": space_id}

        try:
            return self._make_request("GET", endpoint, params=params)
        except GatherIntegrationError as e:
            self._logger.error(f"Guestlist Retrieval Error: {e}")
            raise

    def set_email_guestlist(
        self, 
        space_id: str, 
        guestlist: Dict[str, Dict[str, str]], 
        overwrite: bool = False
    ) -> None:
        """
        Set email guestlist for a space

        Args:
            space_id (str): ID of the space
            guestlist (Dict[str, Dict]): Guestlist to set
            overwrite (bool, optional): Whether to overwrite existing list. Defaults to False.
        """
        endpoint = "/setEmailGuestlist"
        payload = {
            "spaceId": space_id,
            "guestlist": guestlist,
            "overwrite": overwrite
        }

        try:
            self._make_request("POST", endpoint, data=payload)
        except GatherIntegrationError as e:
            self._logger.error(f"Guestlist Update Error: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Replace with actual API key
    API_KEY = os.getenv("GATHER_API_KEY", "your_api_key_here")
    
    try:
        gather_integration = GatherIntegration(API_KEY)
        
        # Example: Create a new space
        new_space_id = gather_integration.create_space(
            name="Court Simulation Space", 
            source_space="your_template_space_id"
        )
        print(f"Created new space: {new_space_id}")
        
    except GatherIntegrationError as e:
        print(f"Integration Error: {e}")
