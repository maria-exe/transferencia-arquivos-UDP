import socket as s
import sys

# requisicao do usuario (@IP_Servidor:Porta_Servidor/nome_do_arquivo.ext)
def file_parser():
    if len(sys.argv) < 2: 
        print("Erro de requisicao: @IP_Servidor:Porta_Servidor/nome_do_arquivo.ext")
        sys.exit(1)
    
    request_file = request_file[1].lstrip("@")
    addr, file_name = file.split("/")
    ip_server, port_server = addr.split(":")

    return int(ip_server), port_server, file_name

# implementar erro de encontrar arquivo


class Client: 
    def __init__(self, ip, port):
        pass


request = input("Digite o destino: ")
path, file = request.strip('@').split('/')
ip_address, port = path.split(':')
        
clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)

message = "Hello World!"
clientSocket.sendto(message.encode(), (ip_address, int(port)))

resp, addr = clientSocket.recvfrom(2048)

print('Servidor:', resp.decode())
clientSocket.close()


