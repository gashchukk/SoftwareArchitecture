import pytest
from fastapi.testclient import TestClient
from logging_service.main import app

client = TestClient(app)

def test_log_message():
    response = client.post("/log", json={"id": "123", "message": "Test Message"})
    assert response.status_code == 200
    assert response.json()["status"] == "Message logged successfully"

def test_log_duplicate_message():
    client.post("/log", json={"id": "123", "message": "Test Message"})
    response = client.post("/log", json={"id": "123", "message": "Test Message"})
    assert response.status_code == 200
    assert response.json()["status"] == "Message already exists. Duplicate message skipped."
