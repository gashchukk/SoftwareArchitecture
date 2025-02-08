# HW Series of Software Architecture Course

Архітектура складається з трьох мікросервисів:
 - facade-service - приймає POST/GET запити від клієнта
 - logging-service - зберігає у пам’яті всі повідомлення які йому надходять, та може повертати їх
 - messages-service - поки виступає у ролі заглушки, при звернені до нього повертає статичне повідомлення

## How to Run:

```
uvicorn facade-service.main:app --reload --port 8000
uvicorn logging-service.main:app --reload --port 8001
uvicorn messages-service.main:app --reload --port 8002
```

### POST Example:
```
curl -X POST "http://localhost:8000/send?msg=Hello%20microservices"
```
### GET Exmaple:
```
curl -X GET "http://localhost:8000/fetch"
```