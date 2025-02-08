from fastapi import FastAPI, HTTPException
from typing import Dict

app = FastAPI()

messages : Dict[str, str] = {

}
@app.post("/log")
def log_message(data : dict):
    message_id, msg = data.get("id"), data.get("message")
    if message_id in messages:
        return {"status": "Message already exists. Duplicate message skipped."}
    messages[message_id] = msg
    print(f"Message logged: {msg}")
    return {"status": "Message logged successfully"}

@app.get("/logs")
def get_logs():
    return list(messages.values())
    