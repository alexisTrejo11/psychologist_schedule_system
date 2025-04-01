from typing import Dict, Any
from datetime import datetime

class ApiResponse:
    """
    Class to standardize API responses.
    """
    @staticmethod
    def format_response(data: Any, success: bool, message: str = "") -> Dict[str, Any]:
        """
        Formats the API response in a consistent manner.

        Args:
            data (Any): The data to include in the response.
            success (bool): Indicates if the operation was successful.
            message (str, optional): An optional message to include in the response. Defaults to "".

        Returns:
            Dict[str, Any]: A dictionary with the standardized response structure, conforming to the following schema:

        Schema:
            {
                "data": {
                    "type": "object",  # or any other type
                    "description": "The data returned by the API call.  The actual structure varies depending on the specific endpoint."
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of the response in ISO 8601 format."
                },
                "success": {
                    "type": "boolean",
                    "description": "Indicates whether the API call was successful."
                },
                "message": {
                    "type": "string",
                    "description": "A human-readable message providing additional information about the response."
                }
            }
        """
        return {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "message": message,
        }
