#!/bin/bash

FACADE_PORT=8000
MESSAGES_PORT1=8001
MESSAGES_PORT2=8005
LOGGING_PORT1=8002
LOGGING_PORT2=8003
LOGGING_PORT3=8004

docker-compose up -d
hz-start
hz-start
hz-start

echo "Starting facade-service on port $FACADE_PORT"
uvicorn facade_service.main:app --host 0.0.0.0 --port $FACADE_PORT &

echo "Starting messages-service on ports $MESSAGES_PORT1 and $MESSAGES_PORT2"
uvicorn messages_service.main:app --host 0.0.0.0 --port $MESSAGES_PORT1 &
uvicorn messages_service.main:app --host 0.0.0.0 --port $MESSAGES_PORT2 &

echo "Starting logging-service on ports $LOGGING_PORT1, $LOGGING_PORT2, $LOGGING_PORT3"
uvicorn logging_service.main:app --host 0.0.0.0 --port $LOGGING_PORT1 &
uvicorn logging_service.main:app --host 0.0.0.0 --port $LOGGING_PORT2 &
uvicorn logging_service.main:app --host 0.0.0.0 --port $LOGGING_PORT3 &

echo "All services are starting..."

wait
