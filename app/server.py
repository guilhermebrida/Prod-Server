import asyncio
import socket
import XVM
import re
import os
import psycopg2
from datetime import datetime
import time

ips = []
LISTENED = []
RSN_DICT = {}
cabeçalho =  'BINAVSFB'
bloc =''
bloco =[]
path = []
path_voz = []
path_script = []
FDIR = []
SFB = []
# # Lê as variáveis de ambiente
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



class MyDatagramProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        self.ids = []

    def datagram_received(self, data, addr):
        self.data = data
        if re.search('BINA.*',data.decode(errors='ignore')) is None:
            if XVM.isValidXVM(data.decode(errors='ignore')):
                xvmMessage = XVM.parseXVM(data.decode(errors='ignore'))
                msg = xvmMessage[0]
                device_id = xvmMessage[1]
                asyncio.create_task(self.handle_request(data, addr, self.transport,device_id))
                if device_id == '0306':
                    print(data)
        if re.search(b'BINA.*',data) is not None:
            print(data)

        
        

# class udp():
    async def handle_request(self,data, addr, transport,device_id):
        self.message = data.decode(errors='ignore')
        if device_id == '0306' and device_id not in LISTENED:
            xvm = XVM.generateXVM(device_id,str(8000).zfill(4),'>QSN<')
            print(xvm)
            transport.sendto(xvm.encode(), addr)
            result = re.search('>RSN.*',self.message)
            if result is not None:
                rsn = result.group()
                self.sn = rsn.split('_')[0].split('>RSN')[1]
                if self.sn:
                    LISTENED.append(device_id)
                    RSN_DICT[device_id]=self.sn
                    print(RSN_DICT)
                    await self.envioScript(transport,addr,device_id)
                    await asyncio.sleep(1)
        if re.search('REP_CFG.*',self.message) is not None and device_id not in SFB:
            SFB.append(device_id)
            rep_cfg = re.search('REP_CFG.*',self.message).group()        
            self.resp_msg = rep_cfg.split('_')[3]
            self.conf = self.resp_msg.split(' ')[0]
            print(self.conf)
            await self.Arquivos(transport,self.message,addr,device_id)
        if re.search('FDIR.*',self.message) is not None:
            if re.search('(FDIR\d{5},).*',self.message) is not None:
                FDIR.append(self.message)
            if re.search('>.*EOF.*',self.message) is not None:
                fdir = re.search('>.*EOF.*',self.message)
                self.vozes = fdir.group().split('_')[2].split(':')[1]
                print('\nFDIR:',self.vozes)
                if int(self.vozes) < 1:
                    await self.reenvio(transport,self.message,addr,device_id)
                else:
                    await self.criar(device_id)

        

        

        
    async def Arquivos(self,transport,message,addr,device_id):
        time_start = time.time()
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
                cs =  await self.crc(sep)
                bloc = bloco+msg+cs
                msg = int(msg,16)+1
                msg = format(msg,'X')
                b = bytes.fromhex(bloc)
                transport.sendto(b, addr)
                await asyncio.sleep(0.3)
            await asyncio.sleep(0.3)
        await self.fdir(transport,addr,device_id)
        print("tempo total:",time.time()-time_start)



    async def crc(self,x): 
        cs_int = 0
        sep = x
        for i in range(len(sep)):
            cs_int ^= (int(sep[i],16)) 
        hexcs = hex(cs_int).replace('0x','')
        return hexcs   
    
    async def criar(self,device_id):
        try:
            sn = RSN_DICT[device_id]
            cursor.execute('INSERT INTO vozes ("IMEI", "SN", "VOZES") values (\'{}\', \'{}\', \'{}\');'.format(device_id, sn,self.vozes))
            connection.commit()
        except:
            pass
        finally:
            cursor.execute('SELECT "IMEI" FROM vozes;')
            results = cursor.fetchall()
            ID = [result[0] for result in results]
            print('Ids no banco:',ID)


    async def fdir(self,transport,addr,device_id):
        try:
            xvm = XVM.generateXVM(device_id,str(8010).zfill(4),'>FDIR<')
            print(xvm)
            transport.sendto(xvm.encode(), addr)
            if re.search('>.*EOF.*',self.message) is not None:
                fdir = re.search('>.*EOF.*',self.message)
                self.vozes = fdir.group().split('_')[2].split(':')[1]
                print('\nFDIR:',self.vozes)
                return self.vozes 
        except:
            raise Exception



    async def envioScript(self,transport,addr,device_id):
        for i in path_script:
            print(i)
            with open(f'{i}') as f:
                self.tudo = f.read()
            self.comandos=(re.findall('(>.*<)', self.tudo))
            for i in range(len(self.comandos)):
                try:
                    xvm = XVM.generateXVM(device_id,str(8010+i).zfill(4),self.comandos[i])
                    transport.sendto(xvm.encode(),addr)
                    await asyncio.sleep(0.1)
                except:
                    raise Exception
        msg = XVM.generateXVM(device_id,str(8100),f'>QEP_CFG<')
        transport.sendto(msg.encode(),addr)



    async def reenvio(self,transport,message,addr,device_id):
            lista_path =[]
            lista = re.findall('\d{8}.MP3', str(FDIR))
            for i in range(len(lista)):
                lista[i]=(''.join(lista[i]).split('.')[0])
            for i in range(len(path_voz)):
                lista_path.append(path_voz[i].split('/')[4].split('_')[0])
            for i in lista:
                for files in lista_path:
                    if i == files:
                        path_voz.pop(lista_path.index(f'{files}'))
                        lista_path.remove(files)
                    else:
                        continue
            print("LISTA PARA REENVIO",path_voz)
            if len(path_voz) != 0:
                print("REENVIANDO.......\n.\n.\n.")
                await self.Arquivos(transport,message,addr,device_id)
            # else:
                # pass



async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MyDatagramProtocol(),
        # local_addr=('192.168.0.116', 65117),
        # local_addr=('192.168.0.116', 10116),
        # local_addr=('127.0.0.11', 10116),
        # local_addr=('191.4.146.247', 10116),
        local_addr=('0.0.0.0', 10116),
        family=socket.AF_INET)
    print(f"Server started on {transport.get_extra_info('sockname')}")
    try:
        while True:
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
    finally:
        transport.close()


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
        cursor.execute('SELECT "IMEI" FROM vozes;')
        results = cursor.fetchall()
        ID = [result[0] for result in results]
        print('Ids no banco:',ID)
        pasta_vozes = "./app/Files/Vozes/"
        pasta_scripts = "./app/Files/Prod_script/"
        path_voz = find(pasta_vozes)
        # print("Arquivos de Voz:",path_voz)
        path = []
        path_script = find(pasta_scripts)
        # print("Script basico:",path_script)
        if path_voz:
            asyncio.run(main())
    except KeyboardInterrupt:
        pass






        # path = dlg.askopenfilenames()
        # nome_arquivo = "00000001_MP3.SFB"
        # for root, dirs, files in os.walk("."):
        #     if nome_arquivo in files:
        #         caminho_arquivo = os.path.join(root, nome_arquivo)
        #         print("Caminho do arquivo encontrado:", caminho_arquivo)
        #         break
        # else:
        #     print("Arquivo não encontrado.")