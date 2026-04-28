import os.path, socket as s
from common import protocolo as p

class Server:
# file
    def __init__(self):
        self.segments = {}
        self.socket = s.socket(s.AF_INET, s.SOCK_DGRAM)

    # verifica se o arquivo existe
    def _verify_request_file(self, filename):
        path = f"./servidor/files/{filename}"
        return os.path.exists(path) and os.path.isfile(path)

    # divisao de arquivos em chuncks - MTU
    def send_file(self, filename):
        pass

    def handle_request(self, filename, addr):
        if self._verify_request_file(filename):
            # self.send_file() # lógica de segmentação dos dados
            self.socket.sendto(0, addr)
            # prossegue com a requisição
            pass
        else: 
            p.error(filename)
            self.in_listen(self)
 
    # em espera pela requisicao do cliente
    def in_listen(self):
        self.socket.bind(('', p.PORT))
        print("Em escuta . . . ")

        while True:
            msg, addr = self.socket.recvfrom(p.MAX_DGRAM)
            type, decoded_msg = p.decode_message(msg)

            print(f"Recebi de {addr}: {decoded_msg}")

            
            # mod_msg = msg.decode().upper()
            # self.socket.sendto(mod_msg.encode(), addr)
 

    def request_file_process():
        pass

    def file_transmission():
        pass


 