from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import httpx
import random
import asyncio
from confluent_kafka import Producer

app = FastAPI()

class Message(BaseModel):
    msg: str

CONFIG_SERVER_URL = "http://127.0.0.1:8005/services"

producer_config = {"bootstrap.servers": "localhost:9092,localhost:9093,localhost:9094"}
producer = Producer(producer_config)

async def get_service_urls(service):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CONFIG_SERVER_URL + f"/{service}")
            response.raise_for_status()
            return response.json().get("ips", [])
        except httpx.RequestError as e:
            print(f"Failed to fetch service addresses from config-server: {e}")
            return []

@app.post("/send")
async def post_request(data: Message):
    new_uuid = str(uuid.uuid4())
    message = {"id": new_uuid, "text": data.msg}
    try:
        producer.produce(
            topic="messages",
            key=new_uuid,
            value=data.text.encode("utf-8")
        )
        producer.flush() 
        print(f"Produced message with ID {new_uuid} to Kafka.")
    except Exception as e:
        print(f"Failed to send message to Kafka: {e}")
        return {"error": "Failed to send message to Kafka"}
    
    logging_service_urls = await get_service_urls("/logging-service")
    shuffled_services = random.sample(logging_service_urls, len(logging_service_urls))

    async with httpx.AsyncClient() as client:
        for selected_service in shuffled_services:
            try:
                response = await client.post(f"{selected_service}/log", json=message)
                response.raise_for_status()
                return {"status": "Message sent successfully", "message_id": new_uuid}
            except httpx.RequestError as e:
                print(f"Request to {selected_service} failed: {e}")
                await asyncio.sleep(1)

    return {"error": "All logging services are unavailable."}

@app.get("/fetch")
async def get_request():
    combined_response = {"logging_messages": [], "messages_service_messages": []}

    logging_service_urls = await get_service_urls("/logging-service")
    shuffled_services = random.sample(logging_service_urls, len(logging_service_urls))

    async with httpx.AsyncClient() as client:
        for selected_service in shuffled_services:
            try:
                logging_response = await client.get(f"{selected_service}/log")
                logging_response.raise_for_status()
                combined_response["logging_messages"] = resp.json().get("messages", [])

                break
            except httpx.RequestError as e:
                print(f"Request to {selected_service} failed: {e}")
                await asyncio.sleep(1)
    messages_service_urls = await get_service_urls("/messages-service")
    shuffled_messages_services = random.sample(messages_service_urls, len(messages_service_urls))
    for url in shuffled_messages_services:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            combined_response["messages_service_messages"] = resp.json().get("messages", [])
            break
        except httpx.RequestError as e:
            print(f"Request to messages service {url} failed: {e}")
            await asyncio.sleep(1)
                
    if not combined_response["logging_messages"] and not combined_response["messages_service_messages"]:
        return {"error": "All services are unavailable."}
    
    return combined_response
