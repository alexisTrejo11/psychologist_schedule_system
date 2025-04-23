from typing import Dict, Any
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from dataclasses import dataclass, asdict

@dataclass
class ApiResponse:
    """
    Dataclass to represent the standardized API response structure.
    """
    data: Any
    timestamp: str
    success: bool
    status_code : int
    message: str


class DjangoResponseWrapper:
    """
    Custom Django Response Wrapper that add to HTTP response theese fields:
        -data = Any 
        -timestamp = date of the request
        -messsage = informative message
        -status_code = http status code 
    """
    @staticmethod
    def found(data=None, entity='Entity', param=None, value=None):
        message = f'{entity} successfully Retreived'
        if param and value:
            message = f'{entity} with {param} [{value}] successfully Retreived'
        
        if isinstance(data, dict):
            data = dict(data)

        reponse_body = ApiResponse(
            data=data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status.HTTP_200_OK,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_200_OK)
    

    @staticmethod
    def success(data=None, message=None):
        if not message:
            message = 'Request Successly Completed'

        if isinstance(data, dict):
            data = dict(data)

        reponse_body = ApiResponse(
            data= data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status.HTTP_200_OK,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_200_OK)
    

    @staticmethod
    def success(data=None, message=None):
        if not message:
            message = 'Request Successly Completed'

        reponse_body = ApiResponse(
            data= data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status.HTTP_200_OK,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_200_OK)
        
    @staticmethod
    def created(data=None, entity=None):
        message = 'Entity Successfully Created'
        if entity:
            message = f'{entity} Successfully Created'

        if isinstance(data, dict):
            data = dict(data)    

        reponse_body = ApiResponse(
            data=data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status.HTTP_201_CREATED,
            message=message
        )

        return Response(data=asdict(reponse_body), status=status.HTTP_201_CREATED)

    @staticmethod
    def updated(data=None, entity=None):
        message = 'Entity Successfully Updated'
        if entity:
            message = f'{entity} Successfully Updated'
        
        if isinstance(data, dict):
            data = dict(data)

        reponse_body = ApiResponse(
            data= data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status.HTTP_200_OK,
            message=message
        )

        return Response(data=asdict(reponse_body), status=status.HTTP_200_OK)


    @staticmethod
    def failure(data=None, message=None, status_code=None):
        if not status_code:
            status_code = status.HTTP_400_BAD_REQUEST

        if isinstance(data, dict):
            data = dict(data)

        if not message:
            message = 'Request Has Fail'

        reponse_body = ApiResponse(
            data= data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status_code,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_200_OK)
    
    @staticmethod
    def not_found(data=None, entity='Entity', param=None, value=None):
        message = f'{entity} not found'
        if param and value:
            message = f'{entity} with {param} [{value}] not found'
        
        if isinstance(data, dict):
            data = dict(data)

        reponse_body = ApiResponse(
            data= data,
            timestamp= datetime.now().isoformat(),
            success= True,
            status_code=status.HTTP_404_NOT_FOUND,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def bad_request(data=None, message=None):
        if not message:
            message = 'Bad Request'

        if isinstance(data, dict):
            data = dict(data)

        reponse_body = ApiResponse(
            data=data,
            timestamp= datetime.now().isoformat(),
            success= False,
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def conflict(message=None):
        if not message:
            message = 'Bad Request'

        reponse_body = ApiResponse(
            data=None,
            timestamp= datetime.now().isoformat(),
            success= False,
            status_code=status.HTTP_409_CONFLICT,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_409_CONFLICT)


    @staticmethod
    def no_content(message=None):
        if not message:
            message = 'No Content'

        reponse_body = ApiResponse(
            data=None,
            timestamp= datetime.now().isoformat(),
            success= False,
            status_code=status.HTTP_204_NO_CONTENT,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def internal_server_error(data=None, message=None):
        if not message:
            message = 'Internal Server Error'

        if isinstance(data, dict):
            data = dict(data)

        reponse_body = ApiResponse(
            data=data,
            timestamp= datetime.now().isoformat(),
            success= False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message
        )
        
        return Response(data=asdict(reponse_body), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
