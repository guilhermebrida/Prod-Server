# Docker 

# Dockerfile
### Define a imagem base, imagem do python 
```docker 
FROM python:3.9-slim-buster
```

### Instala dependências necesárias
```docker 
RUN apt-get update && apt-get install -y libpq-dev python3-tk net-tools lsof && rm -rf /var/lib/apt/lists/* 
``` 

### Define a variável de ambiente para o diretório de trabalho
```docker
ENV APP_HOME /app
WORKDIR $APP_HOME
```

### Copia o requirements.txt e instala as dependências
```docker 
COPY ./app/requirements.txt .
COPY ./app/udp-server.py .
COPY ./app/XVM.py .
RUN pip install --no-cache-dir -r requirements.txt
```

### Copia o código fonte
```docker 
COPY . .
```
### Define as variáveis de ambiente para o banco de dados
```docker
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=postgres
```

### Executa a aplicação
```docker
CMD ["python", "-u","./app/udp-server.py"]
``` 

# Docker compose 
## Services
### App
* build: .: Configura a imagem do serviço a partir do Dockerfile localizado no diretório atual.
* restart: unless-stopped: Essa opção instrui o Docker a reiniciar o serviço automaticamente caso ele seja encerrado, a menos que seja explicitamente parado pelo usuário.
* ports: - "10116:10117/udp": Configura o mapeamento de porta do serviço. Neste exemplo, a porta 10117 do container é mapeada para a porta 10116 do host, usando o protocolo UDP.
* depends_on: - postgres: Configura a dependência do serviço em relação a outro serviço chamado postgres. Isso significa que o serviço atual só será iniciado após a inicialização do serviço postgres.
* environment: - ENDPOINT=postgres: Configura uma variável de ambiente chamada ENDPOINT para o valor postgres.
* links: - postgres: Configura o link para o serviço postgres, permitindo que o serviço atual se conecte ao serviço postgres.
* networks: - backing-services: Configura a rede a ser usada pelo serviço. Neste exemplo, o serviço está configurado para usar a rede chamada backing-services.
```docker 
  app:
    build: .
    restart: unless-stopped
    ports:
      - "10116:10117/udp"
      # - "65117:10117/udp"
    depends_on:
      - postgres
    environment:
      - ENDPOINT=postgres
    links:
      - postgres
    networks:
      - backing-services
```
### Postgres
* image: postgres:14-alpine3.15: Configura a imagem do serviço a ser usada a partir do Docker Hub. Neste exemplo, é usada a imagem postgres:14-alpine3.15, que é uma versão leve do Postgres baseada no Alpine Linux.

* ports: ["5432:5432"]: Configura o mapeamento de porta do serviço. Neste exemplo, a porta 5432 do container é mapeada para a porta 5432 do host.

* restart: always: Configura o comportamento do Docker em relação à reinicialização do serviço. Essa opção instrui o Docker a reiniciar o serviço automaticamente caso ele seja encerrado por algum motivo.

* networks: [backing-services]: Configura a rede a ser usada pelo serviço. Neste exemplo, o serviço está configurado para usar a rede chamada backing-services.

* volumes: - Configura os volumes a serem montados no container do serviço. Neste exemplo, o primeiro volume mapeia o diretório ./app do host para o diretório /data do container. O segundo volume mapeia o arquivo /mnt/c/Python_scripts/Docker-app/docker-app/Docker_python/db/init.sql do host para o diretório /docker-entrypoint-initdb.d/init.sql do container. Isso permite que o arquivo SQL seja executado na inicialização do banco de dados.

* environment: POSTGRES_DB: postgres POSTGRES_USER: postgres POSTGRES_PASSWORD: postgres: Configura as variáveis de ambiente usadas pelo serviço Postgres. indicando o nome do banco de dados, usuário e senha a serem usados. 

```docker 
  postgres: 
    image: postgres:14-alpine3.15
    ports: ["5432:5432"]
    restart: always
    networks: [backing-services] 
    volumes:
      - ./app:/data
      - /mnt/c/Python_scripts/Docker-app/docker-app/Docker_python/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    # hostname: "ec2-3-85-175-98.compute-1.amazonaws.com"
```
### Socat
* image: alpine/socat: Configura a imagem do serviço a ser usada a partir do Docker Hub. Neste exemplo, é usada a imagem alpine/socat, que é uma imagem Alpine do Socat.

* command: socat TCP4-LISTEN:10116,fork,reuseaddr TCP4:127.0.0.1:10117: Configura o comando a ser executado quando o contêiner for iniciado. Neste exemplo, o comando socat é usado para direcionar o tráfego de entrada na porta 10116 para a porta 10117 no endereço IP 127.0.0.1. As opções fork e reuseaddr são usadas para permitir que várias conexões sejam gerenciadas e para reutilizar o endereço IP e a porta.

```docker 
  socat:
    image: alpine/socat
    command: socat TCP4-LISTEN:10116,fork,reuseaddr TCP4:127.0.0.1:10117
    # command: socat TCP4-LISTEN:65117,fork,reuseaddr TCP4:127.0.0.1:10117
```

