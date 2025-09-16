class HttpClientError(Exception):
    """Error genérico de la librería HTTP"""


class HttpRequestError(HttpClientError):
    """Error al hacer la petición HTTP"""
