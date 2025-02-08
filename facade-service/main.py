from fastapi import FastAPI, HTTPException
import requests
import uuid
app = FastAPI()

LOGGING_SERVICE_URL = "http://localhost:8001"
MESSAGES_SERVICE_URL = "http://localhost:8002"

@app.post("/send")
def send(msg : str):
    message_id = str(uuid.uuid4())
    payload = {"id" : message_id,
               "message" : msg}

    try:
        response = requests.post(f"{LOGGING_SERVICE_URL}/log", json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "Message sent successfully", "message_id": message_id}

@app.get("/fetch")
def fetch_messages():
    logging_service_response = requests.get(f"{LOGGING_SERVICE_URL}/logs").text
    msg_service_response = requests.get(f"{MESSAGES_SERVICE_URL}/message").text
    return {"logging_service_response": logging_service_response, "msg_service_response": msg_service_response}
