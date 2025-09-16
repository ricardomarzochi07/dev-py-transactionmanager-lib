from typing import Optional, TypeVar, Generic

T = TypeVar('T')


class HttpResponseSchema(Generic[T]):

    def __init__(self, status_response: bool = False, status_code: int = 0,
                 data: Optional[T] = None, message: Optional[str] = None):
        self.status_response: bool = status_response
        self.status_code: int = status_code
        self.data: Optional[T] = data
        self.message: Optional[str] = message

    def __repr__(self):
        return (f"HttpResponseSchema(status_response={self.status_response}, "
                f"status_code={self.status_code}, data={self.data}, "
                f"message={self.message})")