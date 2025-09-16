import httpx
from typing import Optional, Dict, Any
from buddybet_logmon_common.logger import get_logger
from .constants import Constants
from ..schemas.http_response_schema import HttpResponseSchema
import os


class HttpClient:
    logger = get_logger()

    def __init__(self, base_url: str, timeout: int = 5,
                 default_headers: Optional[Dict[str, str]] = None,
                 cert: Optional[str | tuple] = None,
                 verify: Optional[str | bool] = True):

        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = default_headers or {}

        # Si no es PROD, desactivamos SSL
        app_env = os.getenv("APP_ENV").upper()
        if app_env != Constants.PROD_ENV:
            self.verify = False
            self.cert = None

        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            cert=self.cert,
            verify=self.verify,
            headers=default_headers or {}
        )

    def _request(self, method: str, path: str, **kwargs) -> HttpResponseSchema[Any]:
        headers = kwargs.pop("headers", {})
        combined_headers = {**(self.default_headers or {}), **(headers or {})}

        try:
            response = self.client.request(method, path, headers=combined_headers, **kwargs)
            response.raise_for_status()
            self.logger.info(f"HTTP {method.upper()} {path} -> {response.status_code}")

            return HttpResponseSchema(
                status_response=True,
                status_code=response.status_code,
                data=response.json(),
                message="Request successful"
            )
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return HttpResponseSchema(
                status_response=False,
                status_code=e.response.status_code,
                data=None,
                message=f"HTTP error {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            self.logger.error(f"Request failed: {str(e)}")
            return HttpResponseSchema(
                status_response=False,
                status_code=0,
                data=None,
                message=f"Request failed: {str(e)}"
            )

    def get(self, path: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        return self._request("GET", path, params=params, headers=headers)

    def post(self, path: str, data: Optional[Dict] = None, headers: Optional[Dict] = None):
        return self._request("POST", path, json=data, headers=headers)

    def put(self, path: str, data: Optional[Dict] = None, headers: Optional[Dict] = None):
        return self._request("PUT", path, json=data, headers=headers)

    def delete(self, path: str, headers: Optional[Dict] = None):
        return self._request("DELETE", path, headers=headers)
