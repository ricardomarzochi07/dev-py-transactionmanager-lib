class HttpClientError(Exception):
    """Error genérico de la librería HTTP"""


class HttpRequestError(HttpClientError):
    """Error al hacer la petición HTTP"""


class RequestRetriesExceeded(Exception):
    def __init__(self, message: str = "All HTTP retries failed", cause: Exception = None):
        super().__init__(message)
        self.cause = cause
