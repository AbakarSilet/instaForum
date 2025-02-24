# modelUser/exceptions.py
from rest_framework.exceptions import APIException
from rest_framework import status

class APIError(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        self.detail = {
            "status": self.status_code,
            "message": detail if detail else self.default_detail
        }

class BadRequestError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Requête invalide"

class UnauthorizedError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Non autorisé"

class ForbiddenError(APIError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Accès interdit"

class NotFoundError(APIError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Ressource non trouvée"