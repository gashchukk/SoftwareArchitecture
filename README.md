
# HW 3 Microsevices with Hazelcast

Архітектура тепер складається з чотирьох мікросервисів:
 - facade-service - приймає POST/GET запити від клієнта
 - logging-service - зберігає у пам’яті всі повідомлення які йому надходять, та може повертати їх
 - messages-service - поки виступає у ролі заглушки, при звернені до нього повертає статичне повідомлення
 - config_server - Сервер до якого звертається facade_Service щоб отрмати інофрмацію про IP:port logging_service та messages_service

### Additional tasks
- Implemented Config Server so that Facade can now easily get actual IPs of its microservices
 
## How to Run:

```
chmod +x ./start_services.sh
./start_services.sh
```
<img src="images/run.png">

### Add-ons
Порівняно з попередньою частиною, тепер кожен інстанс logging сервісу піднімає Hazelcast і вони відповідно утворюють кластер


### Testing 
Here in `tests` dir are presented tests wirtten in `pytest` library to test the most generic scenaries:

All of them works well. <br>
**To test by yourself, you can run:**
```
pytest tests/ -v
```
and you will see:
<img src="images/tests.png">

