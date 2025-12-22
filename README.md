# ERPNext Docker Deployment

Custom Docker deployment for ERPNext, including tailored configurations, services, scripts, and environment setup for production and development use.

### Links
- [Frappe Docker Docs](Frappe_Docker.md)
- [User Manual](User_Manual.md)

### Launch ERPNext + Frappe
```bash
$ docker compose up -d

# Verify Deployment
$ docker ps --format "table {{.Names}}\t{{.Status}}"
erpnext-docker-frontend-1      Up 4 minutes
erpnext-docker-scheduler-1     Up 4 minutes
erpnext-docker-db-1            Up 4 minutes (healthy)
erpnext-docker-websocket-1     Up 4 minutes
erpnext-docker-queue-long-1    Up 4 minutes
erpnext-docker-backend-1       Up 4 minutes
erpnext-docker-redis-cache-1   Up 4 minutes
erpnext-docker-queue-short-1   Up 4 minutes
erpnext-docker-redis-queue-1   Up 4 minutes
```

### Initial Setup
- Access ERPNext on http://127.0.0.1:8080/#login
- Default Username: Administrator
- Default Password: admin
- Accounts Passwords can be Changed Later from: http://127.0.0.1:8080/app/user

### Connect to ERPNext Database
```bash
# docker-compose.yml
services:
  db:
    image: mariadb:10.6
    networks:
      - frappe_network
    ports:
      - 3306:3306

$ docker compose down
$ docker compose up -d
# Now MySQL Database is Accessible on tcp://127.0.0.1:3306
```

### ERPNext WebHooks
A webhook is a way for one application to send data over HTTP
to another application automatically when a specific event happens.
- Navigate to `/app/webhook` to Configure ERPNext WebHooks
- WebHook is Attached to Event on a Certain Database Table for Example `on_update`

- Request URL: http://<docker_host_bridge_ip>:port/hook_handler
- Request Method: GET/POST
- JSON Request Body
```js
// Example JSON Request Body DocType: Task
{
    "task_id": "{{ doc.name }}",
    "task_name": "{{ doc.subject }}",
    "project": "{{ doc.project }}",
    "status": "{{ doc.status }}"
}
```

### NodeRED Setup
NodeRED is Used as an Automation Layer for ERPNext WebHooks.
Note That any Custom HTTP Handler can be Used Like Python Fast API for Example.
```bash
# Validate Docker Host Bridge
user@docker-host$ nc -lnvp 16880
Listening on 0.0.0.0 16880

user@docker-host$ docker exec -u root -it erpnext-docker-backend-1 /bin/bash

root@erpnext-docker-backend-1$ apt upate
root@erpnext-docker-backend-1$ apt install netcat-openbsd
root@erpnext-docker-backend-1$ apt install net-tools

root@erpnext-docker-backend-1$ ifconfig 
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.19.0.5  netmask 255.255.0.0  broadcast 172.19.255.255
        ether 02:42:ac:13:00:05  txqueuelen 0  (Ethernet)
        RX packets 50346  bytes 95210868 (90.8 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 56380  bytes 31818822 (30.3 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
# Docker Host IP: 172.19.0.1

root@erpnext-docker-backend-1$ nc 172.19.0.5 16880
# Connection received on 172.19.0.5 38080 @ docker-host

# NodeRED Setup
user@docker-host$ cd nodered
user@docker-host$ npm install
user@docker-host$ npx node-red --port 16880 --userDir .
```
- NodeRED Dashboard Link: http://127.0.0.1:16880/

### Database Modifications - TODO

### Server Modifications - TODO

### Client Modifications - TODO
