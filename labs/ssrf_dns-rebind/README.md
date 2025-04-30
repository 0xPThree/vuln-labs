# SSRF DNS Rebind Attack
## Build Environment
```bash
» docker build -t ssrf-dns-rebind .
[+] Building 45.8s (11/11) FINISHED                                                                                                             docker:default
 => [internal] load build definition from Dockerfile                                                                                                      0.0s
 => => transferring dockerfile: 554B                                                                                                                      0.0s
 => [internal] load metadata for docker.io/library/ubuntu:latest                                                                                          1.7s
 => [internal] load .dockerignore                                                                                                                         0.0s
 => => transferring context: 45B                                                                                                                          0.0s
 => [internal] load build context                                                                                                                         0.0s
 => => transferring context: 12.20kB                                                                                                                      0.0s
 => [1/6] FROM docker.io/library/ubuntu:latest@sha256:1e622c5f073b4f6bfad6632f2616c7f59ef256e96fe78bf6a595d1dc4376ac02                                    4.5s
 => => resolve docker.io/library/ubuntu:latest@sha256:1e622c5f073b4f6bfad6632f2616c7f59ef256e96fe78bf6a595d1dc4376ac02                                    0.0s
 => => sha256:f8b860e4f9036f2694571770da292642eebcc4c2ea0c70a1a9244c2a1d436cd9 424B / 424B                                                                0.0s
 => => sha256:602eb6fb314b5fafad376a32ab55194e535e533dec6552f82b70d7ac0e554b1c 2.30kB / 2.30kB                                                            0.0s
 => => sha256:2726e237d1a374379e783053d93d0345c8a3bf3c57b5d35b099de1ad777486ee 29.72MB / 29.72MB                                                          2.8s
 => => sha256:1e622c5f073b4f6bfad6632f2616c7f59ef256e96fe78bf6a595d1dc4376ac02 6.69kB / 6.69kB                                                            0.0s
 => => extracting sha256:2726e237d1a374379e783053d93d0345c8a3bf3c57b5d35b099de1ad777486ee                                                                 1.6s
 => [2/6] RUN apt-get update -y && apt-get install -y python3 python3-pip python3-venv                                                                   33.0s
 => [3/6] COPY . /webapp                                                                                                                                0.0s 
 => [4/6] WORKDIR /webapp                                                                                                                               0.0s 
 => [5/6] RUN python3 -m venv venv                                                                                                                        2.6s 
 => [6/6] RUN /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt"                                                                  2.3s 
 => exporting to image                                                                                                                                    1.6s 
 => => exporting layers                                                                                                                                   1.6s 
 => => writing image sha256:d88d64dd4af23bef020b56b053c3ca1c6cce56fa08c10f6f347f78b9b531bbcf                                                              0.0s 
 => => naming to docker.io/library/ssrf-dns-rebind

 » docker run -d --name ssrf-dns-rebind -p 8081:80 ssrf-dns-rebind
 » docker container ls                
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS          PORTS                               NAMES
5ec6e76eee9c   ssrf-dns-rebind   "/bin/bash -c 'sourc…"   51 seconds ago   Up 50 seconds   0.0.0.0:80->80/tcp, :::80->80/tcp   ssrf-dns-rebind

» curl -L http://127.0.0.1:8081
<!DOCTYPE html>
<html>
    [...]
</html>
```
