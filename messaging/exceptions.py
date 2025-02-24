class MessagingException(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class UserBlockedException(MessagingException):
    pass

class InvalidReceiverException(MessagingException):
    pass

class UnauthorizedAccessException(MessagingException):
    pass