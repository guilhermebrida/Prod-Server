import socket


HOST = '192.168.0.109'  # Endereço IP do servidor
PORT = 10116  # Porta do servidor

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_socket.bind((HOST, PORT))
print(f"Servidor UDP iniciado em {HOST}:{PORT}")

while True:
    data, address = udp_socket.recvfrom(1024)
    message = data.decode('utf-8')
    print(f"Mensagem recebida de {address[0]}:{address[1]}: {message}")
    response = "Mensagem recebida com sucesso!"
    udp_socket.sendto(response.encode('utf-8'), address)