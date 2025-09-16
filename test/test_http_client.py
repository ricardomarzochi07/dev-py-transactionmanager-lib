import pytest
import httpx
from buddybet_transactionmanager.http.transaction_http import HttpClient
from buddybet_transactionmanager.schemas.http_response_schema import HttpResponseSchema


@pytest.fixture
def client(monkeypatch):
    # Forzamos entorno DEV para desactivar SSL
    monkeypatch.setenv("APP_ENV", "dev")
    return HttpClient(base_url="https://api.test.com")


def test_get_success(client, mocker):
    # Simular respuesta exitosa
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Ricardo"}
    mock_response.raise_for_status.return_value = None

    mocker.patch.object(client.client, "request", return_value=mock_response)

    response = client.get("/users/1")

    assert isinstance(response, HttpResponseSchema)
    assert response.status_response is True
    assert response.status_code == 200
    assert response.data == {"id": 1, "name": "Ricardo"}
    assert response.message == "Request successful"


def test_get_http_error(client, mocker):
    # Simular un error HTTP 404
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=mocker.Mock(), response=mock_response
    )

    mocker.patch.object(client.client, "request", return_value=mock_response)

    response = client.get("/users/999")

    assert isinstance(response, HttpResponseSchema)
    assert response.status_response is False
    assert response.status_code == 404
    assert "HTTP error 404" in response.message


def test_get_request_error(client, mocker):
    # Simular fallo de red
    mocker.patch.object(
        client.client, "request", side_effect=httpx.RequestError("Connection failed")
    )

    response = client.get("/users")

    assert isinstance(response, HttpResponseSchema)
    assert response.status_response is False
    assert response.status_code == 0
    assert "Request failed" in response.message
