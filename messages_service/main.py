from fastapi import FastAPI
from confluent_kafka import Consumer
from threading import Thread
from typing import List

app = FastAPI()

messages: List[str] = []

def consume_messages():
    config = {
        "bootstrap.servers": "localhost:9092,localhost:9093,localhost:9094",
        "group.id": "message-consumer-group",
        "auto.offset.reset": "earliest"
    }
    consumer = Consumer(config)
    consumer.subscribe(["messages"])

    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"[ERROR] {msg.error()}")
            continue
        decoded = msg.value().decode("utf-8")
        print(f"[Kafka] {decoded}")
        messages.append(decoded)

@app.on_event("startup")
def start_consumer():
    thread = Thread(target=consume_messages, daemon=True)
    thread.start()

@app.get("/messages")
def get_messages():
    return {"messages": messages}
