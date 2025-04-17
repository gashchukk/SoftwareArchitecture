import requests

URL_SEND = "http://0.0.0.0:8000/send"
URL_READ = "http://0.0.0.0:8000/fetch"

# Send 10 messages
for i in range(10):
    message ={"msg" : f"msg{i + 1}"}
    response = requests.post(URL_SEND, json=message)
    print(f"Sent: {message}, Status: {response.status_code}")

response = requests.get(URL_READ)
if response.status_code == 200:
    messages = response.json()
    formatted_output = {"messages": messages}
    print(formatted_output)
else:
    print(f"Failed to retrieve messages, Status: {response.status_code}")
