# Banco de Dados

## init.db
* tabela para a inserção dos dados, com exemplo de inserção 
* Colunas:
    - IMEI: o id do copiloto
    - SN: a mensagem coletada pela serial
    - VOZES: quantidade de vozes embarcada no copiloto
    - reception_datetime: data e hora da coleta da mensagem, timezone de São Paulo
```sql
CREATE SCHEMA copilotos;
CREATE TABLE IF NOT EXISTS copilotos.vozes
(
    "IMEI" text COLLATE pg_catalog."default" NOT NULL,
    "SN" text COLLATE pg_catalog."default" NOT NULL,
    "VOZES" bigint
    reception_datetime timestamp with time zone DEFAULT timezone('America/Sao_Paulo', now())
    );
INSERT INTO copilotos.vozes ("IMEI","SN","VOZES") VALUES ('teste','teste1',22);
INSERT INTO copilotos.vozes ("IMEI","SN","VOZES") VALUES ('11111','111111',25);
```