-- CREATE SCHEMA copilotos;
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
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('grafana','grafana',3);
INSERT INTO public.vozes ("IMEI","SN","VOZES") VALUES ('server','graf',19);
