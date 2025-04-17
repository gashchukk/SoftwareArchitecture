from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import httpx
import random
import asyncio

app = FastAPI()

class Message(BaseModel):
    msg: str

CONFIG_SERVER_URL = "http://127.0.0.1:8005/services/logging-service"

async def get_logging_service_urls():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CONFIG_SERVER_URL)
            response.raise_for_status()
            return response.json().get("ips", [])
        except httpx.RequestError as e:
            print(f"Failed to fetch service addresses from config-server: {e}")
            return []

@app.post("/send")
async def post_request(data: Message):
    new_uuid = str(uuid.uuid4())
    message = {"id": new_uuid, "text": data.msg}

    logging_service_urls = await get_logging_service_urls()
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
    logging_service_urls = await get_logging_service_urls()
    shuffled_services = random.sample(logging_service_urls, len(logging_service_urls))

    async with httpx.AsyncClient() as client:
        for selected_service in shuffled_services:
            try:
                logging_response = await client.get(f"{selected_service}/log")
                logging_response.raise_for_status()
                return logging_response.json()
            except httpx.RequestError as e:
                print(f"Request to {selected_service} failed: {e}")
                await asyncio.sleep(1)

    return {"error": "All logging services are unavailable."}
