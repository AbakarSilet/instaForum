# ForumInsta/utils/custom_exception_handler.py

from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        logger.info(f'Exception handled: {exc} with context: {context}')
        
        response.data['status_code'] = response.status_code
        if response.status_code == 400:
            response.data['error'] = 'ValidationSSError'
        if response.status_code == 401:
            response.data['error'] = 'AuthenticationSSError'
        if response.status_code == 403:
            response.data['error'] = 'PermissionError'
        if response.status_code == 404:
            response.data['error'] = 'NotFoundError'
        if response.status_code == 500:
            response.data['error'] = 'ServerError'
    else:
        logger.error(f'Unhandled exception: {exc} with context: {context}')
        
    return response
