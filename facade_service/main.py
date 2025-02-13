from fastapi import FastAPI, HTTPException
import requests
import uuid
from pydantic import BaseModel
import time

app = FastAPI()

LOGGING_SERVICE_URL = "http://localhost:8001"

class Message(BaseModel):
    msg: str

@app.post("/send")
def send(message: Message):
    message_id = str(uuid.uuid4())
    payload = {"id": message_id, "message": message.msg}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{LOGGING_SERVICE_URL}/log", json=payload)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail="Logging service unavailable")
            time.sleep(1)
    return {"status": "Message sent successfully", "message_id": message_id}

@app.get("/fetch")
def fetch_messages():
    
    logging_service_response = requests.get(f"{LOGGING_SERVICE_URL}/logs").text
    msg_service_response = requests.get(f"{MESSAGES_SERVICE_URL}/message").text
    return {"logging_service_response": logging_service_response, "msg_service_response": msg_service_response}
