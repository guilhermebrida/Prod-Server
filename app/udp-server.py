import asyncio
import socket
import XVM
import re
from tkinter import filedialog as dlg
import mysql.connector
from mysql.connector import Error
import psycopg2


ips = []
ALREADY_LISTEN = []
RSN_DICT = {}
VOZ = []
cabeçalho =  'BINAVSFB'
bloc =''
bloco =[]



ENDPOINT="ec2-52-91-118-43.compute-1.amazonaws.com"
PORT="5432"
USER="postgres"
# REGION="us-east-2a"
DBNAME="gb"

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
            cursor.execute(f'INSERT INTO gb.copilotos (IMEI, SN, FDIR) VALUES ("{device_id}","{sn2}","{self.vozes}");')
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
        local_addr=('192.168.0.116', 10116),
        # local_addr=('', 10116),
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
        cursor.execute('SELECT * FROM gb.vozes;')
        result = cursor.fetchall()
        print(result)
        path = dlg.askopenfilenames()
        if path:
            asyncio.run(main())
    except KeyboardInterrupt:
        pass




















# import asyncio
# import socket
# import XVM

# class MyDatagramProtocol(asyncio.DatagramProtocol):
#     def connection_made(self, transport):
#         self.transport = transport
#         self.ids = []

#     def datagram_received(self, data, addr):
#         asyncio.create_task(handle_request(data, addr, self.transport))

# async def handle_request(data, addr, transport):
    
#     message = data.decode(errors='ignore')
#     print(f"Received message from {addr}: {message}")
#     if XVM.isValidXVM(message):
#         xvmMessage = XVM.parseXVM(message)
#         msg = xvmMessage[0]
#         device_id = xvmMessage[1]
#         response = XVM.generateXVM(device_id,str(8000).zfill(4),'>QSN<')
#         await asyncio.sleep(1) # Simulando uma resposta demorada
#         transport.sendto(response.encode(), addr)
#         print(f"Sent response to {addr}: {response}")


# async def main():
#     loop = asyncio.get_running_loop()
#     transport, protocol = await loop.create_datagram_endpoint(
#         lambda: MyDatagramProtocol(),
#         local_addr=('192.168.0.116', 10116),
#         family=socket.AF_INET)
#     print(f"Server started on {transport.get_extra_info('sockname')}")

#     try:
#         while True:
#             await asyncio.sleep(0.1)
#     except asyncio.CancelledError:
#         pass
#     finally:
#         transport.close()

# if __name__ == "__main__":
#     try:
#         ips = []
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         pass
