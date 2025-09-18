from typing import Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')


class HttpResponseSchema(BaseModel, Generic[T]):
    status_response: bool = False
    status_code: int = 0
    data: Optional[T] = None
    message: Optional[str] = None

    def __repr__(self):
        return (f"HttpResponseSchema(status_response={self.status_response}, "
                f"status_code={self.status_code}, data={self.data}, "
                f"message={self.message})")
