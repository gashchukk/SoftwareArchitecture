from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import httpx
import random
import asyncio
from confluent_kafka import Producer

from consul_service import (
    register_service,
    deregister_service,
    discover_service,
    get_kv,
)

app = FastAPI()

CONSUL_HOST     = "localhost"
SERVICE_NAME    = "facade-service"
SERVICE_PORT    = 8000
SERVICE_ID      = f"{SERVICE_NAME}-{uuid.uuid4()}"

KV_KAFKA_BOOT   = "config/kafka/bootstrap"
KV_MQ_QUEUE     = "config/mq/queue_name"


@app.on_event("startup")
async def on_startup():
    register_service(CONSUL_HOST, SERVICE_NAME, SERVICE_ID, SERVICE_PORT)

    bootstrap = get_kv(CONSUL_HOST, KV_KAFKA_BOOT)
    print(f"[DEBUG] Kafka bootstrap.servers = {bootstrap!r}")
    app.state.producer = Producer({"bootstrap.servers": bootstrap})

@app.on_event("shutdown")
async def on_shutdown():
    deregister_service(CONSUL_HOST, SERVICE_ID)
    app.state.producer.flush(10.0)


class Message(BaseModel):
    msg: str


producer_config = {"bootstrap.servers": "localhost:29092,localhost:29093,localhost:29094"}
producer = Producer(producer_config)

async def get_service_urls(service :str ):
    instances = discover_service(CONSUL_HOST, service)
    urls = []
    for inst in instances:
        host = inst.get("ServiceAddress") or inst.get("Address")
        port = inst["ServicePort"]
        urls.append(f"http://{host}:{port}")
    return urls

@app.post("/send")
async def post_request(data: Message):
    new_uuid = str(uuid.uuid4())
    message = {"id": new_uuid, "msg": data.msg}
    try:
        producer.produce(
            topic="messages",
            key=message["id"].encode("utf-8"),
            value=message["msg"].encode("utf-8"),
        )
        producer.flush() 
        print(f"Produced message with ID {new_uuid} to Kafka.")
    except Exception as e:
        print(f"Failed to send message to Kafka: {e}")
        return {"error": "Failed to send message to Kafka"}
    
    logging_service_urls = await get_service_urls("logging-service")
    shuffled_services = random.sample(logging_service_urls, len(logging_service_urls))

    async with httpx.AsyncClient() as client:
        for selected_service in shuffled_services:
            try:
                response = await client.post(f"{selected_service}/log", json=message)
                response.raise_for_status()
                return {"status": "Message sent successfully", "message_id": new_uuid}
            except httpx.RequestError as e:
                print(f"Request to {selected_service} failed: {e}")
                await asyncio.sleep(0.5)

    return {"error": "All logging services are unavailable."}

@app.get("/fetch")
async def get_request():
    combined_response = {"logging_messages": [], "messages_service_messages": []}

    logging_service_urls = await get_service_urls("logging-service")
    shuffled_services = random.sample(logging_service_urls, len(logging_service_urls))

    async with httpx.AsyncClient() as client:
        for selected_service in shuffled_services:
            try:
                logging_response = await client.get(f"{selected_service}/log")
                logging_response.raise_for_status()
                combined_response["logging_messages"] = logging_response.json()
                break  
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"Request to {selected_service} failed: {e}")
                await asyncio.sleep(1)

        messages_service_urls = await get_service_urls("messages-service")
        shuffled_messages_services = random.sample(messages_service_urls, len(messages_service_urls))

        for url in shuffled_messages_services:
            try:
                resp = await client.get(f"{url}/messages")
                resp.raise_for_status()
                combined_response["messages_service_messages"] = resp.json()
                break
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"Request to messages service {url} failed: {e}")
                await asyncio.sleep(1)

    if not combined_response["logging_messages"] and not combined_response["messages_service_messages"]:
        return {"error": "All services are unavailable."}

    return combined_response
