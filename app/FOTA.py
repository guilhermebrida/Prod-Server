import asyncio
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

def enviar_bloco(sock, bloco, endereco):
    sock.sendto(bloco, endereco)
    response, _ = sock.recvfrom(1024)
    print('Resposta do equipamento:', response.decode())

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









# class MyDatagramProtocol(asyncio.DatagramProtocol):
#     def connection_made(self, transport):
#         self.transport = transport
#         self.ids = []

#     def datagram_received(self, data, addr):
#         self.data = data
#         self.addr = addr
#         sn = None
#         if re.search(b'BINA.*',self.data) is not None:
#             print(data)
#         if re.search(b'BINA.*',self.data) is None:
#             xvmMessage = XVM.parseXVM(self.data.decode())
#             msg = xvmMessage[0]
#             self.device_id = xvmMessage[1]
#             if self.device_id in ID and not ALREADY_LISTEN:
#                 sn = self.core()
#             if sn is not None and self.device_id in ID:
#                 arquivos = self.Arquivos()
#                 if arquivos is not None:
#                     for b in arquivos:
#                         self.transport.sendto(b, self.addr)
#                         time.sleep(0.5)

        
            




#         # asyncio.create_task(udp().handle_request(data, addr, self.transport))

#     def core(self):
#         if re.search(b'BINA.*',self.data) is None:
#             xvm = XVM.generateXVM(self.device_id,str(8000).zfill(4),'>QSN<')
#             print(xvm)
#             self.transport.sendto(xvm.encode(), self.addr)
#             result = re.search(b'>RSN.*',self.data)
#             if result is not None:
#                 rsn = result.group().decode()
#                 self.sn = rsn.split('_')[0].split('>RSN')[1]
#                 print(self.sn)
#                 ALREADY_LISTEN.append(self.device_id)
#                 print(ALREADY_LISTEN)
#                 return self.sn
            

#     def Arquivos(self):
#         # VOZ.append(device_id)
#         for files in path:
#             print(files)
#             f=open(f'{files}','rb')
#             conteudo = f.read()
#             separar = [conteudo[i:i+520]for i in range(0,len(conteudo),520)]
#             print('\n',files,'\n')
#             msg = '80000000'
#             for i in range(len(separar)):
#                 bloco = cabeçalho.encode().hex()+separar[i].hex()+self.sn.encode().hex()
#                 sep = re.findall('........',bloco)
#                 sep.append(msg)
#                 cs =  self.crc(sep)
#                 bloc = bloco+msg+cs
#                 msg = int(msg,16)+1
#                 msg = format(msg,'X')
#                 b = bytes.fromhex(bloc)
#                 # print(b)
#                 blocos_envio.append(b)
#                 # self.transport.sendto(b, self.addr)
#                 # await self.datagram_received()
#                 # time.sleep(1)
#                 # await asyncio.sleep(0.5)
#         return blocos_envio

#     def crc(self,x): 
#         cs_int = 0
#         sep = x
#         for i in range(len(sep)):
#             cs_int ^= (int(sep[i],16)) 
#         hexcs = hex(cs_int).replace('0x','')
#         return hexcs   


# async def main():
#     loop = asyncio.get_running_loop()
#     transport, protocol = await loop.create_datagram_endpoint(
#         lambda: MyDatagramProtocol(),
#         local_addr=('192.168.0.116', 10116),
#         # local_addr=('192.168.0.116', 10116),
#         # local_addr=('127.0.0.11', 10116),
#         # local_addr=('191.4.146.247', 10116),
#         # local_addr=('0.0.0.0', 10117),
#         family=socket.AF_INET)
#     print(f"Server started on {transport.get_extra_info('sockname')}")

#     try:
#         while True:
#             await asyncio.sleep(0.1)
#     except asyncio.CancelledError:
#         pass
#     finally:
#         transport.close()


# def find():
#     pasta = "./app/Vozes/"
#     arquivos = os.listdir(pasta)
#     for arquivo in arquivos:
#         print('puro',arquivo)
#         caminho_arquivo = os.path.join(pasta, arquivo)
#         if os.path.isfile(caminho_arquivo):
#             print(caminho_arquivo)
#             path.append(caminho_arquivo)
#     return path



# if __name__ == "__main__":
#     try:
#         ID.append(input('Qual ID será atualizado?'))
#         # path = find()
#         path = ['./app/Vozes/00000002_MP3.SFB']
#         if path:
#             asyncio.run(main())
#     except KeyboardInterrupt:
#         pass