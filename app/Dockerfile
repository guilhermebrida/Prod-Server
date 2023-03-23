FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y git \
    # && git clone https://github.com/guilhermebrida/Docker_python.git \
    && apt-get install -y python3-pip 
    # && pip install -r /app/Docker_python/requirements.txt

EXPOSE 8080

CMD ["python","./app/Docker_python/udp.server.py"]

