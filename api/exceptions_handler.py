from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data['status_code'] = response.status_code
        if response.status_code == 400:
            response.data['error'] = 'ValidationError'
        if response.status_code == 401:
            response.data['error'] = 'AuthenticationError'
        if response.status_code == 403:
            response.data['error'] = 'PermissionError'
        if response.status_code == 404:
            response.data['error'] = 'NotFoundError'
        if response.status_code == 500:
            response.data['error'] = 'ServerError'
    return response
