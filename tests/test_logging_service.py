import pytest
from fastapi.testclient import TestClient
from logging_service.main import app, messages_map

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def clear_messages_map_before_tests():
    messages_map.clear()

def test_log_message():
    response = client.post("/log", json={"id": "123", "text": "Test Message"})
    assert response.status_code == 200
    assert response.json()["status"] ==  "Message logged successfully"

def test_log_duplicate_message():
    client.post("/log", json={"id": "123", "text": "Test Message"})
    response = client.post("/log", json={"id": "123", "text": "Test Message"})
    assert response.status_code == 200
    assert response.json()["status"] == "Message already exists. Duplicate message skipped."
