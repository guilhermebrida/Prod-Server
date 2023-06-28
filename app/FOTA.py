import socket
import XVM
import re
import psycopg2
import os
import time
import threading

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



host = '0.0.0.0'
porta = 10116
equipamentos_executados = {}
blocos_de_dados = [...]  


def Arquivos(device_id):
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


def solicitar_serial_number(sock, device_id, addr):
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

# def enviar_linha_script(sock, linha, endereco):
#     sock.sendto(linha.encode(), endereco)
#     response, _ = sock.recvfrom(1024)
#     print('Resposta do equipamento:', response)

def envioScript(sock, addr, device_id):
    for i in path_script:
        print(i)
        with open(f'{i}') as f:
            tudo = f.read()
        comandos = re.findall('(>.*<)', tudo)
        for i in range(len(comandos)):
            try:
                xvm = XVM.generateXVM(device_id, str(8010+i).zfill(4), comandos[i])
                sock.sendto(xvm.encode(), addr)
                response, _ = sock.recvfrom(1024)
                print('Resposta do equipamento:', response.decode())
                time.sleep(0.1)
            except:
                raise Exception
    msg = XVM.generateXVM(device_id, str(8100), f'>QEP_CFG<')
    sock.sendto(msg.encode(), addr)

def enviar_bloco(sock, bloco, endereco):
    sock.sendto(bloco, endereco)
    response, _ = sock.recvfrom(1024)
    print('Resposta do equipamento:', response)

def servidor_udp():
    global equipamentos_executados
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, porta))
    print('Servidor UDP iniciado.')
    while True:
        data, addr = sock.recvfrom(1024)
        ip_equipamento = addr[0]
        if ip_equipamento not in equipamentos_executados:
            print('Equipamento', ip_equipamento, 'conectado.')
            if XVM.isValidXVM(data.decode(errors='ignore')):
                xvmMessage = XVM.parseXVM(data.decode(errors='ignore'))
                msg = xvmMessage[0]
                device_id = xvmMessage[1]
                solicitar_serial_number(sock, device_id, addr)
                envioScript(sock, device_id, addr)
                blocos_de_dados = Arquivos(device_id)
                for bloco in blocos_de_dados:
                    thread = threading.Thread(target=enviar_bloco, args=(sock, bloco, addr))
                    thread.start()
                    thread.join()
                equipamentos_executados[ip_equipamento] = True
        print(data)



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
            servidor_udp()
    except KeyboardInterrupt:
        pass






