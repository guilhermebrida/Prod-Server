# UDP server
* Arquivo udp-server.py


## Lê as variáveis de ambiente do dockerfile
```python
    postgres_host = os.environ['POSTGRES_HOST']
    postgres_port = os.environ['POSTGRES_PORT']
    postgres_user = os.environ['POSTGRES_USER']
    postgres_password = os.environ['POSTGRES_PASSWORD']
    postgres_db = os.environ['POSTGRES_DB']
```

## Conecta ao banco 
* Usa as variáveis de ambiente para se conectar ao banco de dados
```python
connection = psycopg2.connect(
    host=postgres_host,
    port=postgres_port,
    user=postgres_user,
    password=postgres_password,
    dbname=postgres_db
)
    cursor = connection.cursor() 
```
## Criação do Server UDP 
* A função datagram_received ao receber uma mensagem e caso o prefixo da mensagem nao comece com BINA (protocolo SFB) irá chamar a função parseXVM que faz o parser das mensagens caso esteja no formato XVM
* Em seguida chama a função handle_request da classe udp, que precisa da mensagem(data), do ip de origem (addr), o objeto que faz o envio das mensagens (transport) e o device_id
* Utilzei o device '0306' para o exemplo, caso as mensagens que chegam sejam dele, irá printar na tela para debug
* Caso as mensagens contenham o prefixo BINA a mensagem é printada 
```python
class MyDatagramProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        self.ids = []

    def datagram_received(self, data, addr):
        if re.search('BINA.*',data.decode(errors='ignore')) is None:
            if XVM.isValidXVM(data.decode(errors='ignore')):
                xvmMessage = XVM.parseXVM(data.decode(errors='ignore'))
                msg = xvmMessage[0]
                device_id = xvmMessage[1]
                asyncio.create_task(udp().handle_request(data, addr, self.transport,device_id))
                if device_id == '0306':
                    print(data)
        if re.search(b'BINA.*',data) is not None:
            print(data)
```
## Classe udp
### Função Handle_request 
* A função handle_request da classe udp recebe os parametros já mencionados
* Caso a mensagem recebida seja de um device que não esteja na lista LISTENED e também nao esteja na lista de IDs no banco de dados irá enviar o comando >QSN< para capturar o SN do equipamento, utilizando a função generateXVM que deixa no protocolo XVM
* Em seguida envia a mensagem utilizando o transport.sendto para o ip do device (addr)
* Ao receber a resposta que irá começar com >RSN, salva na vairavel sn, e adiciona o device_id na lista de devices ja escutados (LISTENED) e também no dicionário RSN_DICT
* Em seguida chama uma sequencia de outras funções da classe udp (envioScript,Arquivos,fdir)
    - envioScript, Envia os comandos do script basico do copiloto
    - Arquivos, Envia os arquivos de audio
    - fdir, Confere quantas vozes o equipamento possui embarcado
* Ao final da função fdir, caso a mensagem que chegue contenha EOF é capturada dentro dessa mensagem o numero de vozes embarcado no equipamento
* No final do processo é chamada a função criar que faz o insert no banco 
```python
class udp():
    async def handle_request(self,data, addr, transport,device_id):
        self.message = data.decode(errors='ignore')
        if device_id == '0306' and not LISTENED and not ID:
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
                    await self.Arquivos(transport,self.message,addr,device_id)
                    await self.fdir(transport,addr,device_id)
        if re.search('>.*EOF.*',self.message) is not None:
            fdir = re.search('>.*EOF.*',self.message)
            self.vozes = fdir.group().split('_')[2].split(':')[1]
            print('\nFDIR:',self.vozes)
            await self.criar(device_id)
```

### Função Arquivos 
* Essa função lê os arquivos de audio, utilizando o caminho para os mesmos, contido na variavel path_voz e formata no seguindo o protocolo SFB
* Para cada bloco de 520 bytes, a função monta os blocos com o cabeçalho + conteudo + SN do equipamento + numero da msg(começando em 80000000) + cs (função para calcular o crc)
* Usa a transport.sendto para enviar cada bloco de bytes para o endereço do equipamento e aguarda 0.5s para receber o ACK de resposta
###### Envio de SFB
* Pacotes de 520 bytes consecutivos são capturados do arquivo .SFB em que os primeiros 4 bytes são o 
endereço de memória e os últimos 4 bytes são o chksum dos dados.
Sendo então os pacotes a enviar para o dispositivo compostos da seguinte forma:
    - Cabeçalho BINAVSFB (8 bytes)
    - Dados SFB (520 bytes)
    - Número de série do equipamento (8 bytes)
    - Nº de mensagem (4 bytes)
    - Chksum (4 bytes)
```python
    async def Arquivos(self,transport,message,addr,device_id):
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
                await asyncio.sleep(0.5)
```


### Função crc
* Função que calcula o checksum de cada bloco de mensagem do protocolo SFB
```python 
    async def crc(self,x): 
        cs_int = 0
        sep = x
        for i in range(len(sep)):
            cs_int ^= (int(sep[i],16)) 
        hexcs = hex(cs_int).replace('0x','')
        return hexcs   
```
### Função criar
* Função que faz o insert dos dados do equipamento no bando de dados
    - coluna IMEI recebe device_id
    - coluna SN recebe o SN do copiloto
    - coluna VOZES recebe a quantidade de vozes embarcadas no equipamento
```python 
    async def criar(self,device_id):
        try:
            sn = RSN_DICT[device_id]
            cursor.execute('INSERT INTO copilotos.vozes ("IMEI", "SN", "VOZES") \
                            values (\'{}\', \'{}\', \'{}\');'.format(device_id, sn,self.vozes))
            connection.commit()
        except:
            pass
```
### Função fdir
* Envia o comando >FDIR< para o copiloto, no formato XVM utilizando a função generareXVM
```python 
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
```
### Função envioScript
* Le o conteudo do arquivo, que o diretório esta salvo na variavel path_script, filtra apenas os comandos, estão entre ><
* Faz o envio dos comandos, no formato XVM e utilizando o transport.sendto 
```python 
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
                except:
                    raise Exception
```


## Função main
* Função assincrona que cria um endpoint de datagrama, que recebe dois argumentos a função MyDatagramProtocol e o endereço para vincular o servidor, no caso está no (0.0.0.0 na porta 10117) dentro do container, comentando, outros exemplos de ip e porta para utilizar
```python 
async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MyDatagramProtocol(),
        # local_addr=('192.168.0.116', 65117),
        # local_addr=('192.168.0.116', 10116),
        # local_addr=('127.0.0.11', 10116),
        # local_addr=('191.4.146.247', 10116),
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
```

## Função find
* Função que procura todos os arquivos dentro de um local, que é passado como argumento (pasta). E os salva dentro da lista path
```python 
def find(pasta):
    arquivos = os.listdir(pasta)
    for arquivo in arquivos:
        print('puro',arquivo)
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo):
            print(caminho_arquivo)
            path.append(caminho_arquivo)
    return path
```

## Inicialização do Script
* Faz um select no banco e coleta todos os device_id que já inseridos (ID), para se os mesmo enviarem mensagem para o servidor, não serem reconfigurados
* path_voz chama a função find e passa o caminho para os arquivos de voz, e a função retorna a lista dos arquivos dentro do diretório
* path_script chama a função find e passa o caminho para o script basico, e a função retorna a lista do arquivo dentro do diretório
```python 
if __name__ == "__main__":
    try:
        cursor.execute('SELECT "IMEI" FROM copilotos.vozes;')
        results = cursor.fetchall()
        ID = [result[0] for result in results]
        print('Ids no banco:',ID)
        pasta_vozes = "./app/Files/Vozes/"
        pasta_scripts = "./app/Files/Prod_script/"
        path_voz = find(pasta_vozes)
        print("Arquivos de Voz:",path_voz)
        path = []
        path_script = find(pasta_scripts)
        print("Script basico:",path_script)
        if path_voz:
            asyncio.run(main())
    except KeyboardInterrupt:
        pass
```
