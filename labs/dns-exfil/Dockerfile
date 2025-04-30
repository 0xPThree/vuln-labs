FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv dnsutils curl base58 iptables && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN python3 -m venv /app/venv
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chown -R www-data:www-data /app
RUN chmod +x start.sh

CMD ./start.sh