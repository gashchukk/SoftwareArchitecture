#!/bin/bash

FACADE_PORT=8000
MESSAGES_PORT=8001
LOGGING_PORT1=8002
LOGGING_PORT2=8003
LOGGING_PORT3=8004
CONFIG_PORT=8005

uvicorn facade_service.main:app --host 0.0.0.0 --port $FACADE_PORT &

uvicorn messages_service.main:app --host 0.0.0.0 --port $MESSAGES_PORT &

uvicorn logging_service.main:app --host 0.0.0.0 --port $LOGGING_PORT1 &
uvicorn logging_service.main:app --host 0.0.0.0 --port $LOGGING_PORT2 &
uvicorn logging_service.main:app --host 0.0.0.0 --port $LOGGING_PORT3 &

uvicorn config_server.main:app --host 0.0.0.0 --port $CONFIG_PORT &
wait
