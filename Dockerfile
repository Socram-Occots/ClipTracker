# Dockerfile
FROM python:3.12.8

RUN apt-get update && apt-get install -y \
    xvfb python3-tk x11vnc fluxbox && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 5900

ENTRYPOINT ["/start.sh"]