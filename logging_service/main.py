from fastapi import FastAPI
from pydantic import BaseModel
import hazelcast
import os
import uuid

from consul_service import (
    register_service,
    deregister_service,
    get_kv,
)

CONSUL_HOST      = "localhost"
SERVICE_NAME     = "logging-service"
SERVICE_PORT     = int(os.getenv("LOGGING_PORT", 8002))
SERVICE_ID       = f"{SERVICE_NAME}-{uuid.uuid4()}"

KV_HZ_MEMBERS    = "config/hazelcast/members"
KV_HZ_CLUSTER    = "config/hazelcast/cluster"


app = FastAPI()

@app.on_event("startup")
async def on_startup():
    register_service(CONSUL_HOST, SERVICE_NAME, SERVICE_ID, SERVICE_PORT)
    members_csv = get_kv(CONSUL_HOST, KV_HZ_MEMBERS)
    cluster_name = get_kv(CONSUL_HOST, KV_HZ_CLUSTER)
    members = [m.strip() for m in members_csv.split(",") if m.strip()]

    app.state.hz = hazelcast.HazelcastClient(
        cluster_members=members,
        cluster_name=cluster_name
    )
    app.state.map = app.state.hz.get_map("hdmap").blocking()


@app.on_event("shutdown")
async def on_shutdown():
    deregister_service(CONSUL_HOST, SERVICE_ID)
    await app.state.hz.shutdown()


hazelcast_client = hazelcast.HazelcastClient(
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"]
)
messages_map = hazelcast_client.get_map("hdmap").blocking()

class RequestModel(BaseModel):
    id: str
    msg: str


@app.post("/log")
async def log_message(data : RequestModel):
    message_id, msg = data.id, data.msg
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
