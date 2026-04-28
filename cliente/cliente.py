import socket as s
import os, sys
from common import protocolo as p

# requisicao do usuario (@IP_Servidor:Porta_Servidor/nome_do_arquivo.ext)
def file_parser():
    if len(sys.argv) < 2: 
        print("Erro de requisicao: @IP_Servidor:Porta_Servidor/nome_do_arquivo.ext")
        sys.exit(1)
    
    request_file = sys.argv[1].lstrip("@")
    addr, file_name = request_file.split("/")
    ip_server, port_server = addr.split(":")

    return ip_server, int(port_server), file_name

# implementar erro de encontrar arquivo

class Client: 
    def __init__(self):
        self.socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.segments = {} 
        self.total_segments = None

    def send_request(self, ip, port, file_name):
        message = p.get(file_name)
        self.socket.sendto(message, (ip, port))


        resp, addr = self.clientSocket.recvfrom(p.MAX_DGRAM)

        print('Servidor:', resp.decode())
        self.socket.close()

    def verify_integrity(self):
        pass

    def mount_segment(self):
        pass

    def save_file(self, filename, mount_data):
        folder = "./cliente/downloads/"
        os.makedirs(folder, exist_ok=True)
        
        full_path = os.path.join(folder, filename)

        try:
            with open(full_path, "wb") as f:
                f.write(mount_data)
                print("Arquivo salvo com sucesso!")
        
        except OSError as e:
            print(f"Erro ao salvar arquivo: {e}")


    
    # simulacao de perda de pacote
    # solicitar retransmissão de arquivos