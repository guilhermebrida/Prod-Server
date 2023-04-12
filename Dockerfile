# FROM python:3

# WORKDIR /app

# RUN apt-get update && apt-get install -y git \
#     # && git clone https://github.com/guilhermebrida/Docker_python.git \
#     && apt-get install -y python3-pip 
#     # && pip install -r /app/Docker_python/requirements.txt

# EXPOSE 8080

# CMD ["python","./app/Docker_python/udp.server.py"]




# Define a imagem base
FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y libpq-dev python3-tk net-tools lsof && rm -rf /var/lib/apt/lists/* 

# Define a variável de ambiente para o diretório de trabalho
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copia o requirements.txt e instala as dependências
COPY ./app/requirements.txt .
COPY ./app/udp-server.py .
COPY ./app/XVM.py .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY . .

# Copia o arquivo init.db para o diretório de inicialização do banco de dados
# COPY ./init.db /docker-entrypoint-initdb.d/init.db

# Define as variáveis de ambiente para o banco de dados
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=postgres

# Expõe a porta para a aplicação
# EXPOSE 10116/udp

# Executa a aplicação

CMD ["python", "-u","./app/udp-server.py"]

