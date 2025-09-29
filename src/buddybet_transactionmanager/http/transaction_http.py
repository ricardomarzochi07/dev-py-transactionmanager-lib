import httpx
from typing import Optional, Dict, Any
from buddybet_logmon_common.logger import get_logger
from .constants import Constants
from .exceptions import RequestRetriesExceeded
from ..schemas.http_response_schema import HttpResponseSchema
import os
import json


class HttpClient:
    logger = get_logger()

    def __init__(
        self,
        base_url: str,
        timeout: int = 5,
        default_headers: Optional[Dict[str, str]] = None,
        cert: Optional[str | tuple] = None,
        verify: Optional[str | bool] = True
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = default_headers or {}

        app_env = os.getenv("APP_ENV", "").upper()
        if app_env != Constants.PRO_ENV:
            self.verify = False
            self.cert = None
        else:
            self.verify = verify
            self.cert = cert

        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            cert=self.cert,
            verify=self.verify,
            headers=self.default_headers
        )

    def _parse_json_response(self, response: httpx.Response) -> Optional[Any]:
        try:
            content_type = response.headers.get("Content-Type", "").lower()
            if response.content and ("json" in content_type or "+json" in content_type):
                return response.json()
        except json.JSONDecodeError:
            self.logger.warning(f"No se pudo decodificar JSON: {response.content}")
        return None

    def _request(self, method: str, path: str, **kwargs) -> HttpResponseSchema[Any]:
        headers = kwargs.pop("headers", {})
        combined_headers = {**(self.default_headers or {}), **(headers or {})}
        last_exception = None

        for attempt in range(1, Constants.RETRIES + 1):
            try:
                response = self.client.request(method, path, headers=combined_headers, **kwargs)

                # Intentamos parsear el contenido antes de levantar la excepción
                data = self._parse_json_response(response)

                # Levantar excepción si el status no fue 2xx
                response.raise_for_status()

                self.logger.info(f"HTTP {method.upper()} {path} -> {response.status_code}")
                return HttpResponseSchema(
                    status_response=True,
                    status_code=response.status_code,
                    data=data,
                    message="Request successful"
                )

            except httpx.HTTPStatusError as e:
                error_data = self._parse_json_response(e.response)
                self.logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                return HttpResponseSchema(
                    status_response=False,
                    status_code=e.response.status_code,
                    data=error_data,
                    message=f"HTTP error {e.response.status_code}: {e.response.text}"
                )

            except httpx.RequestError as e:
                self.logger.warning(f"Attempt {attempt}/{Constants.RETRIES} failed: {str(e)}")
                last_exception = e

        raise RequestRetriesExceeded(
            message=f"Request failed after {Constants.RETRIES} attempts: {str(last_exception)}",
            cause=last_exception
        )

    def get(self, path: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        return self._request("GET", path, params=params, headers=headers)

    def post(self, path: str, data: Optional[Dict] = None, json_data: Optional[Any] = None,
             headers: Optional[Dict] = None, files: Optional[Dict] = None):
        if json_data is not None:
            return self._request("POST", path, json=json_data, headers=headers)
        elif files is not None:
            return self._request("POST", path, files=files, data=data, headers=headers)
        else:
            return self._request("POST", path, data=data, headers=headers)

    def put(self, path: str, data: Optional[Dict] = None, headers: Optional[Dict] = None):
        return self._request("PUT", path, json=data, headers=headers)

    def delete(self, path: str, headers: Optional[Dict] = None):
        return self._request("DELETE", path, headers=headers)
