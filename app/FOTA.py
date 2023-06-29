import socket
import XVM
import re
import psycopg2
import os
import time
import threading
import asyncio
import selectors
import time

ips = []
ALREADY_LISTEN = []
RSN_DICT = {}
VOZ = []
cabeçalho =  'BINAVSFB'
bloc =''
bloco =[]
path = []
ID=[]
blocos_envio = []
arquivos = None
BLOCOS = []
LISTENED = []

postgres_host = os.environ['POSTGRES_HOST']
postgres_port = os.environ['POSTGRES_PORT']
postgres_user = os.environ['POSTGRES_USER']
postgres_password = os.environ['POSTGRES_PASSWORD']
postgres_db = os.environ['POSTGRES_DB']

connection = psycopg2.connect(
    host=postgres_host,
    # host="postgres",
    port=postgres_port,
    user=postgres_user,
    password=postgres_password,
    dbname=postgres_db
)

cursor = connection.cursor()


host = '0.0.0.0'
porta = 10116
equipamentos_executados = {}
blocos_de_dados = [...]  


async def Arquivos(device_id):
        print(device_id)
        sn = RSN_DICT[device_id]
        print(path_voz)
        for files in path_voz:
            f=open(f'{files}','rb')
            conteudo = f.read()
            separar = [conteudo[i:i+520]for i in range(0,len(conteudo),520)]
            print('\n',files,'\n')
            msg = '80000000'
            for i in range(len(separar)):
                bloco = cabeçalho.encode().hex()+separar[i].hex()+sn.encode().hex()
                sep = re.findall('........',bloco)
                sep.append(msg)
                cs =  crc(sep)
                bloc = bloco+msg+cs
                msg = int(msg,16)+1
                msg = format(msg,'X')
                b = bytes.fromhex(bloc)
                BLOCOS.append(b)
        return BLOCOS



def crc(x): 
    cs_int = 0
    sep = x
    for i in range(len(sep)):
        cs_int ^= (int(sep[i],16)) 
    hexcs = hex(cs_int).replace('0x','')
    return hexcs   

def find(pasta):
    arquivos = os.listdir(pasta)
    print(arquivos)
    for arquivo in arquivos:
        # print('puro',arquivo)
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo):
            path.append(caminho_arquivo)
    return path


async def enviar_bloco(sock, bloco, endereco):
    sock.sendto(bloco, endereco)
    # await asyncio.wait_for(receber_resposta(sock), timeout=3)
    receber_resposta(sock)
    

async def solicitar_serial_number(sock, device_id, addr):
    xvm = XVM.generateXVM(device_id, str(8000).zfill(4), '>QSN<')
    print(xvm)
    sock.sendto(xvm.encode(), addr)
    response, _ = sock.recvfrom(1024)
    result = re.search('>RSN.*', response.decode())
    if result is not None:
        rsn = result.group()
        sn = rsn.split('_')[0].split('>RSN')[1]
        if sn:
            LISTENED.append(device_id)
            RSN_DICT[device_id] = sn
    # await asyncio.wait_for(receber_resposta(sock), timeout=3)
    # receber_resposta(sock)
    

async def envioScript(sock, device_id, addr):
    
    for i in path_script:
        with open(f'{i}') as f:
            tudo = f.read()
        comandos = re.findall('(>.*<)', tudo)
        for i in range(len(comandos)):
            tentativas = 0
            try:
                xvm = XVM.generateXVM(device_id, str(8010+i).zfill(4), comandos[i])
                sock.sendto(xvm.encode(), addr)
                # await asyncio.wait_for(receber_resposta(sock), timeout=3)
                while receber_resposta(sock) is False:
                    print('tentei')
                    sock.sendto(xvm.encode(), addr)
                    if True:
                        break
            except asyncio.TimeoutError:
                tentativas += 1
                print(tentativas)
    msg = XVM.generateXVM(device_id, str(8100), f'>QEP_CFG<')
    sock.sendto(msg.encode(), addr)

def receber_resposta(sock):
    timeout = 5
    start_time = time.time()
    response, _ = sock.recvfrom(1024)
    if time.time() - start_time >= timeout:
        return False
    print('Resposta:', response)


            
async def fdir(sock, device_id, addr):
    try:
        xvm = XVM.generateXVM(device_id,str(8010).zfill(4),'>FDIR<')
        print(xvm)
        sock.sendto(xvm.encode(), addr)
        response, _ = sock.recvfrom(1024)
        if re.search('>.*EOF.*',response.decode()) is not None:
            fdir = re.search('>.*EOF.*',response.decode())
            fdir = fdir.group().split('_')[2].split(':')[1]
            print('\nFDIR:',fdir)
            return fdir 
    except:
        raise Exception

async def criar(device_id,vozes):
    try:
        sn = RSN_DICT[device_id]
        cursor.execute('INSERT INTO vozes ("IMEI", "SN", "VOZES") values (\'{}\', \'{}\', \'{}\');'.format(device_id, sn,vozes))
        connection.commit()
    except:
        pass
    finally:
        cursor.execute('SELECT "IMEI" FROM vozes;')
        results = cursor.fetchall()
        ID = [result[0] for result in results]
        print('Ids no banco:',ID)

async def main():
    socket.setdefaulttimeout(5)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, porta))
    while True:
        print('aqui')
        if TimeoutError:
            continue
        data, addr = sock.recvfrom(1024)
        ip_equipamento = addr[0]
        if ip_equipamento not in equipamentos_executados:
            if XVM.isValidXVM(data.decode(errors='ignore')):
                xvmMessage = XVM.parseXVM(data.decode(errors='ignore'))
                msg = xvmMessage[0]
                device_id = xvmMessage[1]
                await solicitar_serial_number(sock, device_id, addr)
                await envioScript(sock, device_id, addr)
                blocos_de_dados = await Arquivos(device_id)
                for bloco in blocos_de_dados:
                    await enviar_bloco(sock, bloco, addr)
                vozes = await fdir(sock, device_id, addr)
                if vozes is not None:
                    if int(vozes) < 1:
                        await criar(device_id,vozes)
                else:
                    vozes = await fdir(sock, device_id, addr)
                equipamentos_executados[ip_equipamento] = True
        print('Mensagem recebida:', data.decode())




if __name__ == "__main__":
    try:
        pasta_vozes = "./app/Files/Vozes/"
        pasta_scripts = "./app/Files/Prod_script/"
        path_voz = find(pasta_vozes)
        # print("Arquivos de Voz:",path_voz)
        path = []
        path_script = find(pasta_scripts)
        # print("Script basico:",path_script)
        if path_voz:
            asyncio.run(main())
            # servidor_udp()
    except KeyboardInterrupt:
        pass







# def solicitar_serial_number(sock, device_id, addr):
#     xvm = XVM.generateXVM(device_id, str(8000).zfill(4), '>QSN<')
#     print(xvm)
#     sock.sendto(xvm.encode(), addr)
#     response, _ = sock.recvfrom(1024)
#     result = re.search('>RSN.*', response.decode())
#     if result is not None:
#         rsn = result.group()
#         sn = rsn.split('_')[0].split('>RSN')[1]
#         if sn:
#             LISTENED.append(device_id)
#             RSN_DICT[device_id] = sn

# def envioScript(sock, device_id, addr):
#     for i in path_script:
#         with open(f'{i}') as f:
#             tudo = f.read()
#         comandos = re.findall('(>.*<)', tudo)
#         for i in range(len(comandos)):
#             try:
#                 xvm = XVM.generateXVM(device_id, str(8010+i).zfill(4), comandos[i])
#                 sock.sendto(xvm.encode(), addr)
#                 response, _ = sock.recvfrom(1024)
#                 print('Resposta do equipamento:', response.decode())
#                 time.sleep(0.1)
#             except:
#                 raise Exception
#     msg = XVM.generateXVM(device_id, str(8100), f'>QEP_CFG<')
#     sock.sendto(msg.encode(), addr)

# def enviar_bloco(sock, bloco, endereco):
#     sock.sendto(bloco, endereco)
#     response, _ = sock.recvfrom(1024)
#     print('Resposta do equipamento:', response)

# def servidor_udp():
#     global equipamentos_executados
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind((host, porta))
#     print('Servidor UDP iniciado.')
#     while True:
#         data, addr = sock.recvfrom(1024)
#         ip_equipamento = addr[0]
#         if ip_equipamento not in equipamentos_executados:
#             print('Equipamento', ip_equipamento, 'conectado.')
#             if XVM.isValidXVM(data.decode(errors='ignore')):
#                 xvmMessage = XVM.parseXVM(data.decode(errors='ignore'))
#                 msg = xvmMessage[0]
#                 device_id = xvmMessage[1]
#                 print(device_id)
#                 solicitar_serial_number(sock, device_id, addr)
#                 envioScript(sock, device_id, addr)
#                 blocos_de_dados = Arquivos(device_id)
#                 for bloco in blocos_de_dados:
#                     thread = threading.Thread(target=enviar_bloco, args=(sock, bloco, addr))
#                     thread.start()
#                     thread.join()
#                 equipamentos_executados[ip_equipamento] = True
#         print(data)

