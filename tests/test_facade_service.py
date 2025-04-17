import requests
import pytest

URL_SEND = "http://0.0.0.0:8000/send"
URL_READ = "http://0.0.0.0:8000/fetch"



@pytest.mark.parametrize("message", [f"Test message {i + 1}" for i in range(10)])
def test_send_message(message):
    response = requests.post(URL_SEND, json={"msg": message})
    assert response.status_code == 200, f"Failed to send message: {message}"

def test_fetch_messages():
    response = requests.get(URL_READ)
    assert response.status_code == 200, "Failed to retrieve messages"
    messages = response.json()
    formatted_output = {"messages": messages}
    print(formatted_output)
    assert len(messages) > 0, "No messages received"

