from fastapi import FastAPI
from confluent_kafka import Consumer
from typing import List
import uuid
import threading
import os
import os
import uuid
import os

app = FastAPI()

from consul_service import (
    register_service,
    deregister_service,
    get_kv,
)

CONSUL_HOST      = "localhost"
SERVICE_NAME     = "messages-service"
SERVICE_PORT     = int(os.getenv("MESSAGES_PORT", 8001))
SERVICE_ID       = f"{SERVICE_NAME}-{uuid.uuid4()}"

KV_KAFKA_BOOT    = "config/kafka/bootstrap"
KV_MQ_TOPIC      = "config/mq/queue_name"

messages: List[str] = []

@app.on_event("startup")
def on_startup():
    register_service(CONSUL_HOST, SERVICE_NAME, SERVICE_ID, SERVICE_PORT)

    bootstrap = get_kv(CONSUL_HOST, KV_KAFKA_BOOT)
    topic     = get_kv(CONSUL_HOST, KV_MQ_TOPIC)
    
    consumer_conf = {
        "bootstrap.servers": bootstrap,
        "group.id": SERVICE_ID,
        "auto.offset.reset": "earliest"
    }
    app.state.topic    = topic
    app.state.consumer = Consumer(consumer_conf)
    app.state.consumer.subscribe([topic])

    app.state.messages = []
    def poll_loop():
        while True:
            msg = app.state.consumer.poll(timeout=0.5)
            if msg is None:
                continue
            if msg.error():
                print(f"[Kafka ERROR] {msg.error()}")
                continue
            text = msg.value().decode("utf-8")
            print(f"[Kafka] {text}")
            app.state.messages.append(text)
    t = threading.Thread(target=poll_loop, daemon=True)
    app.state._poll_thread = t
    t.start()


@app.on_event("shutdown")
def on_shutdown():
    deregister_service(CONSUL_HOST, SERVICE_ID)
    app.state.consumer.close()


@app.get("/messages")
def get_messages():
    return {"messages": app.state.messages}
