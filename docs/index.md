# Autoconfiguração dos Copilotos
* ***Documentação para da aplicação em python para autoconfiguração dos copilotos em produção***
* **Nessa aplicação é utilizado um instancia ubuntu da AWS e nela foi criado 3 containers utilizando docker, um serviço com a aplicação em python, um banco postgres e também Grafana**


## Bibliotecas Python
* `import asyncio` - Biblioteca para codigo assíncrono
* `import socket` - Biblioteca para criar server UDP
* `import XVM`  - Biblioteca para formatação do XVM (linguagem do copiloto)
* `import re` - Biblioteca para utilizar expressão regular
* `import psycopg2` - Biblioteca para se conectar no banco postgres
* `import os` - Biblioteca para interagir com o sistema operacional


## Comandos Docker 

### Rodar aplicação
* levantar as aplicações do docker compose

```docker compose up --build```

### Apagar aplicação
* Apaga as aplicações e também remove a suas imagens geradas no build

```docker compose down --rmi all```    

### Remover todos os containers
``` docker rm $(docker ps -a)``` 

### Remover todos as imagens
```docker rmi $(docker images -q)``` 

### Subir apenas o Banco Postgres
```docker compose -f docker-compose.yml up -d```

### Subir apenas a aplicação Python
```docker compose -f server-prod.yml up --build```


## Configuração dos Copilotos
* Enviar arquivo de APN correspondente ao SIM Card inserido no Copliloto

### Configurar IP do server
* apontar o copiloto para o IP da maquina na AWS (caso interrompa o a maquina o IP muda, e deve ser reconfigurado no copiloto)

```VSIP0,54.207.138.190.4096.10116```


## Configuração da EC2 da AWS

* Maquina t2.micro ubuntu
* Liberar acesso UDP na porta 10116
* Liberar acesso TCP 3000(grafana) e 5432(postgres) ou todos TCP
<!-- ![Imagem de como configurar o banco postgres no grafana](C:\Users\guilh\OneDrive\Área de Trabalho\configurar_banco_grafana.png) -->

## Grafana

No Grafana apenas precisa configurar o Database do Postgres, inserir o IP da maquina da AWS porta 5432, Database, user e password desta aplicação é "postgres" e marcar TLS como disable


