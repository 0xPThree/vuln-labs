# DNS Exfiltration
## Build Environment
We setup the Docker container using `--add-host attacker.com:172.17.0.1` to simulate that we, as an attacker, own the domain attacker.com.

In order to apply iptables rules we also need the flag `--cap-add=NET_ADMIN`, we use this to minimize the attack surface instead of using e.g `--privileged`.

```bash
» docker build -t dns-exfil .                                                                               
» docker run -d --name dns-exfil --cap-add=NET_ADMIN --add-host attacker.com:172.17.0.1 -p 8081:80 dns-exfil

» docker container ls                                                                                       
CONTAINER ID   IMAGE       COMMAND                  CREATED              STATUS              PORTS                                   NAMES
87e3168ad02c   dns-exfil   "/bin/sh -c ./iptabl…"   About a minute ago   Up About a minute   0.0.0.0:8081->80/tcp, :::8081->80/tcp   dns-exfil
 ```

<details>
  <summary><b>Spoiler</b></summary>

If everything works as intended we should have a Flask app running as `www-data`, vulnerable to command injection by chaining commands. 

```bash
root@87e3168ad02c:/app# iptables -L
Chain INPUT (policy DROP)
target     prot opt source               destination         
ACCEPT     udp  --  anywhere             anywhere            
ACCEPT     all  --  anywhere             anywhere            
ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
ACCEPT     tcp  --  anywhere             anywhere             multiport dports 49335:49354

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy DROP)
target     prot opt source               destination         
ACCEPT     udp  --  anywhere             anywhere            
ACCEPT     tcp  --  anywhere             anywhere             tcp spt:http
ACCEPT     tcp  --  anywhere             anywhere             multiport sports 49335:49354

root@87e3168ad02c:/app# ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0   2800  1684 ?        Ss   08:34   0:00 /bin/sh -c ./iptables-rules.sh
root           7  0.0  0.0   4332  2772 ?        S    08:34   0:00 su -s /bin/bash www-data -c /app/venv/bin/python3 /app/app.py
www-data      20  0.1  0.3 186316 31784 ?        Ss   08:34   0:00 /app/venv/bin/python3 /app/app.py
root          35  0.0  0.0   4588  3664 pts/0    Ss   08:35   0:00 /bin/bash
root          49  0.0  0.0   7888  4124 pts/0    R+   08:36   0:00 ps aux
```
</details>
