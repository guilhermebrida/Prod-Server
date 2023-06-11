# FROM python:3.9-slim-buster

# RUN apt-get update && apt-get install -y libpq-dev python3-tk net-tools lsof && rm -rf /var/lib/apt/lists/* 

# ENV APP_HOME /app
# WORKDIR $APP_HOME

# COPY ./app/requirements.txt .
# COPY ./app/udp-server.py .
# COPY ./app/XVM.py .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# # ENV POSTGRES_HOST=localhost
# ENV POSTGRES_HOST=postgres
# ENV POSTGRES_PORT=5432
# ENV POSTGRES_USER=postgres
# ENV POSTGRES_PASSWORD=postgres
# ENV POSTGRES_DB=postgres

# CMD ["python", "-u","./app/udp-server.py"]



#############
# Imagem base
FROM ubuntu:latest

# Instala as dependências necessárias
RUN apt-get update && apt-get install -y curl && \
    apt-get install -y libfontconfig1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define a versão do Grafana
ENV GRAFANA_VERSION 8.0.6

# Baixa e instala o Grafana
RUN curl -LO https://dl.grafana.com/oss/release/grafana_${GRAFANA_VERSION}_amd64.deb && \
    dpkg -i grafana_${GRAFANA_VERSION}_amd64.deb && \
    rm grafana_${GRAFANA_VERSION}_amd64.deb

# Expõe a porta padrão do Grafana
EXPOSE 3000

# Comando para iniciar o Grafana
CMD ["grafana-server", "--config=/etc/grafana/grafana.ini"]







