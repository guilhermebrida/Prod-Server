import asyncio
import socket
import XVM
import re
from tkinter import filedialog as dlg
import mysql.connector
from mysql.connector import Error
import psycopg2
import os


ips = []
ALREADY_LISTEN = []
RSN_DICT = {}
VOZ = []
cabeçalho =  'BINAVSFB'
bloc =''
bloco =[]

# Lê as variáveis de ambiente
# postgres_host = os.environ['POSTGRES_HOST']
# postgres_port = os.environ['POSTGRES_PORT']
# postgres_user = os.environ['POSTGRES_USER']
# postgres_password = os.environ['POSTGRES_PASSWORD']
# postgres_db = os.environ['POSTGRES_DB']

# print('HOST:{}  PORTA:{}   DB:{}  USER:{}  PASS:{} '.format(postgres_host,postgres_port,postgres_db,postgres_user,postgres_password))

# Usa as variáveis de ambiente para se conectar ao banco de dados
# connection = psycopg2.connect(
#     # host=postgres_host,
#     host="postgres",
#     port=postgres_port,
#     user=postgres_user,
#     password=postgres_password,
#     dbname=postgres_db
# )

#CONECTA COM BANCO REAL
# ENDPOINT="ec2-52-91-118-43.compute-1.amazonaws.com"
# PORT="5432"
# USER="postgres"
# # REGION="us-east-2a"
# DBNAME="gb"

#CONECT COM LOCALHOST NA MÃO
ENDPOINT="postgres"
# ENDPOINT="localhost"
PORT="5432"
USER="postgres"
DBNAME="postgres"
connection = psycopg2.connect(host=ENDPOINT, user=USER, password='postgres', port=PORT, database=DBNAME)
cursor = connection.cursor()



class MyDatagramProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        self.ids = []

    def datagram_received(self, data, addr):
        # if re.search(b'RGP.*',data) is None:
        print(data)
        asyncio.create_task(udp().handle_request(data, addr, self.transport))
        
        

class udp():
    async def handle_request(self,data, addr, transport):
        transport = transport
        self.message = data.decode(errors='ignore')
        if re.search('BINA.*',self.message) is None:
            if XVM.isValidXVM(self.message):
                xvmMessage = XVM.parseXVM(self.message)
                msg = xvmMessage[0]
                device_id = xvmMessage[1]
                if device_id not in ALREADY_LISTEN:
                    xvm = XVM.generateXVM(device_id,str(8000).zfill(4),'>QSN<')
                    print(xvm)
                    transport.sendto(xvm.encode(), addr)
                    result = re.search('>RSN.*',self.message)
                    if result is not None:
                        rsn = result.group()
                        self.sn = rsn.split('_')[0].split('>RSN')[1]
                        if self.sn:
                            ALREADY_LISTEN.append(device_id)
                            RSN_DICT[device_id]=self.sn
                            print(RSN_DICT)
                            await self.Arquivos(transport,self.message,addr,device_id)
                            await self.fdir(transport,addr,device_id)
        
                if re.search('>.*EOF.*',self.message) is not None:
                    fdir = re.search('>.*EOF.*',self.message)
                    self.vozes = fdir.group().split('_')[2].split(':')[1]
                    print('\nFDIR:',self.vozes)
                    print(RSN_DICT)
                    print(device_id)
                    await self.criar(device_id)
                    print('feito')
        

        
    async def Arquivos(self,transport,message,addr,device_id):
        sn = RSN_DICT[device_id]
        VOZ.append(device_id)
        for files in path:
            f=open(f'{files}','rb')
            conteudo = f.read()
            separar = [conteudo[i:i+520]for i in range(0,len(conteudo),520)]
            print('\n',files,'\n')
            msg = '80000000'
            for i in range(len(separar)):
                bloco = cabeçalho.encode().hex()+separar[i].hex()+sn.encode().hex()
                sep = re.findall('........',bloco)
                sep.append(msg)
                cs =  await self.crc(sep)
                bloc = bloco+msg+cs
                msg = int(msg,16)+1
                msg = format(msg,'X')
                b = bytes.fromhex(bloc)
                transport.sendto(b, addr)
                await asyncio.sleep(0.5)




    async def crc(self,x): 
        cs_int = 0
        sep = x
        for i in range(len(sep)):
            cs_int ^= (int(sep[i],16)) 
        hexcs = hex(cs_int).replace('0x','')
        return hexcs   
    
    async def criar(self,device_id):
        try:
            print('dict',RSN_DICT)
            sn2 = RSN_DICT[device_id]
            sn = RSN_DICT.get(device_id, 'nao encontrado')
            cursor.execute(f'INSERT INTO copilotos.vozes (IMEI, SN, FDIR) VALUES ("{device_id}","{sn2}","{self.vozes}");')
            connection.commit()
        except:
            pass


    async def fdir(self,transport,addr,device_id):
        try:
            xvm = XVM.generateXVM(device_id,str(8010).zfill(4),'>FDIR<')
            print(xvm)
            transport.sendto(xvm.encode(), addr)
            if re.search('>.*EOF.*',self.message) is not None:
                fdir = re.search('>.*EOF.*',self.message)
                self.vozes = fdir.group().split('_')[2].split(':')[1]
                print('\nFDIR:',self.vozes)
                # fdir = re.search(b'>.*EOF.*',self.resposta_fdir)
                return self.vozes 
        except:
            raise Exception

async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MyDatagramProtocol(),
        # local_addr=('192.168.0.116', 10116),
        # local_addr=('127.0.0.11', 10116),
        local_addr=('0.0.0.0', 10117),
        family=socket.AF_INET)
    print(f"Server started on {transport.get_extra_info('sockname')}")

    try:
        while True:
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
    finally:
        transport.close()





if __name__ == "__main__":
    try:
        cursor.execute('SELECT * FROM copilotos.vozes;')
        result = cursor.fetchall()
        print(result)
        # path = dlg.askopenfilenames()
        path = 'C:\\Python scripts\\server-UDP\\udp\\app-docker\\Docker_python\\app\\Vozes\\00000001_MP3.SFB'
        if path:
            asyncio.run(main())
    except KeyboardInterrupt:
        pass




# import socket

# UDP_IP = "0.0.0.0"
# UDP_PORT = 10117

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((UDP_IP, UDP_PORT))

# print("Server listening on port", UDP_PORT)

# while True:
#     data, addr = sock.recvfrom(1024)
#     print("Received message:", data.decode())
