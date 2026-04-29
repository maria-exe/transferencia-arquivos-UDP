import os, sys, socket as s, threading, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import protocolo as p

class Server:
# file
    def __init__(self):
        self.segments = {}
        self.socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.socket.bind(('', p.PORT))

    # verifica se o arquivo existe
    def _verify_request_file(self, file_name):
        path = os.path.join(os.path.dirname(__file__), 'files', file_name)
        return os.path.exists(path) and os.path.isfile(path)

    # divisao de arquivos em chuncks - MTU
    def send_file(self, file_name, addr):
        path = os.path.join(os.path.dirname(__file__), 'files')

        file_size = os.path.getsize(os.path.join(path, file_name))
        total_segments = math.ceil(file_size/p.MSS)
        seq_num = 0

        self.segments[addr] = {}        

        with open(os.path.join(path, file_name), "rb") as f:
            chunk = f.read(p.MSS)
            while chunk:                              
                segment = p.make_pkt(seq_num, chunk, total_segments)
                self.segments[addr][seq_num] = segment
                package = p.pack_pkt(segment)
                self.socket.sendto(package, addr)
                
                seq_num += 1
                chunk = f.read(p.MSS)
                
     
    def handle_request(self, data, addr):
            request_type, decoded_data = p.decode_message(data)

            if request_type == "GET": 
                if self._verify_request_file(decoded_data):# se o arquivo existe
                    self.send_file(decoded_data, addr)
                
                else: 
                    self.send_error(decoded_data, addr)
        
            elif request_type == "RTS":
                self.retransmit_data(decoded_data, addr)

            else: 
                print("Mensagem desconhecida")
 
    def send_error(self, data, addr):
        self.socket.sendto(p.error(data), addr)
        
    def in_listen(self):
        print("Em escuta . . . ")
        
        while True:
            data, addr = self.socket.recvfrom(p.MAX_DGRAM)
            thread = threading.Thread (
            target=self.handle_request,
            args=(data, addr) )
            
            thread.start()

    def retransmit_data(self, missing_segments, addr): 
        if addr not in self.segments:
            print(f"Nenhuma sesssao ativa para {addr}")
            return    
                     
        for seg in missing_segments:
            if self.segments[addr].get(seg) is not None:
                package = p.pack_pkt(self.segments[addr][seg])
                self.socket.sendto(package, addr)
            else:
                print(f"Segmento: {seg} nao foi encontrado.")
                
                           

# instancia do servidor
if __name__ == "__main__":
    server = Server()
    server.in_listen()
   


 