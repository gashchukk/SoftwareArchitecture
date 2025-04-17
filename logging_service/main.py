from fastapi import FastAPI
from pydantic import BaseModel
import hazelcast

app = FastAPI()

hazelcast_client = hazelcast.HazelcastClient(
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"]
)
messages_map = hazelcast_client.get_map("hdmap").blocking()

class RequestModel(BaseModel):
    id: str
    text: str


@app.post("/log")
async def log_message(data : RequestModel):
    message_id, msg = data.id, data.text
    if messages_map.contains_key(message_id):
        return {"status": "Message already exists. Duplicate message skipped."}
    messages_map.put(message_id, msg)
    print(f"Message logged: {msg}")
    return {"status": "Message logged successfully"}

@app.get("/log")
async def get_logs():
    return list(messages_map.values())

@app.delete("/log")
async def clear_logs():
    messages_map.clear()
    return {"status": "All messages cleared successfully"}
