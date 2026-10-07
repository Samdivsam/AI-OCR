class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__("AUTHENTICATION_FAILED", message, 401)


class AuthorizationError(AppException):
    def __init__(self, message: str = "You do not have access to this resource.") -> None:
        super().__init__("AUTHORIZATION_FAILED", message, 403)


class BadRequestError(AppException):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message, 400)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__("NOT_FOUND", message, 404)


class ProcessingError(AppException):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message, 422)

