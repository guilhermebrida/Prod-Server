# Autoconfiguração dos Copilotos
* ***Documentação para da aplicação em python para autoconfiguração dos copilotos em produção***
* **Nessa aplicação é criado 3 containers utilizando docker, um serviço com a aplicação em python, um banco postgres e um serviço para redirecionar as mensagens UDP que chegam para o ip do container**


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


