# Banco de Dados

## init.db
* tabela para a inserção dos dados, com exemplo de inserção 
* Colunas:
    - IMEI: o id do copiloto
    - SN: a mensagem coletada pela serial
    - VOZES: quantidade de vozes embarcada no copiloto
    - reception_datetime: data e hora da coleta da mensagem, timezone de São Paulo
```sql
CREATE TABLE IF NOT EXISTS public.vozes
(
    "IMEI" text COLLATE pg_catalog."default" NOT NULL,
    "SN" text COLLATE pg_catalog."default" NOT NULL,
    "VOZES" bigint,
    reception_datetime timestamp with time zone DEFAULT timezone('America/Sao_Paulo', now())
    );
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('teste','teste',22);
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('teste2','teste2',25);
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('teste3','teste3',12);
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('teste4','teste4',3);
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('teste5','teste5',19);
```