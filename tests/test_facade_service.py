import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from facade_service.main import app
from requests.exceptions import HTTPError

client = TestClient(app)

def test_send_message_success():

    with patch('facade_service.main.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = client.post("/send", json={"msg": "Test message"})
        assert response.status_code == 200
        assert response.json()["status"] == "Message sent successfully"

def test_send_message_retry():

    with patch('facade_service.main.requests.post') as mock_post:
        mock_response_failure = Mock()
        mock_response_failure.raise_for_status.side_effect = HTTPError("Service unavailable")
        mock_response_success = Mock()
        mock_response_success.status_code = 200

        mock_post.side_effect = [mock_response_failure, mock_response_success]

        response = client.post("/send", json={"msg": "Test message"})
        assert response.status_code == 200
        assert response.json()["status"] == "Message sent successfully"

def test_send_message_failure():

    with patch('facade_service.main.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("Service unavailable")
        mock_post.side_effect = [mock_response, mock_response, mock_response]

        response = client.post("/send", json={"msg": "Test message"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Logging service unavailable"
