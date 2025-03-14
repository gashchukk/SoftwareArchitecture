from fastapi import FastAPI
import json

app = FastAPI()

with open("config_server/services_config.json", "r") as file:
    services = json.load(file)

@app.get("/services/{service_name}")
def get_service_ips(service_name: str):
    service_ips = services.get(service_name)
    if service_ips:
        return {"ips": service_ips}
    return {"error": "Service not found"}