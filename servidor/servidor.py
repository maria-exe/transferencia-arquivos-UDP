import os, sys, socket as s, threading, math
from pathlib import Path


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import protocolo as p

class Server:
# file
    def __init__(self):
        self.segments = {}
        self.ack = {}
        self.ack_events = {}
        self.socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.socket.bind(('', p.PORT))

    def in_listen(self):
        print("Em escuta . . . ")
        
        while True:
            data, addr = self.socket.recvfrom(p.MAX_DGRAM)
            thread = threading.Thread (
            target=self.handle_request,
            args=(data, addr) )
            
            thread.start()

    # verifica se o arquivo existe
    def _verify_request_file(self, file_name):
        path = Path(__file__).parent / 'files' / file_name
        return path.is_file()
    
  
    # processa requisicao do cliente
    def handle_request(self, data, addr):
        request_type, decoded_data = p.decode_message(data)

        if request_type == "GET": 
            if self._verify_request_file(decoded_data): # se o arquivo existe, envia ele
                self.send_file(decoded_data, addr)
                
            else: 
                error_msg = p.error(decoded_data)       # envia mensagem de erro definida no protocolo
                self.socket.sendto(error_msg, addr)    
        
        elif request_type == "RTS":
            self.retransmit_data(decoded_data, addr)

        elif request_type == "ACK":
            self.ack[addr] = decoded_data
            
            if addr in self.ack_events:
                self.ack_events[addr].set()

        else: 
            pass   


    def send_file(self, file_name, addr):
        path = os.path.join(os.path.dirname(__file__), 'files', file_name)

        file_size = os.path.getsize(path)
        total_segments = math.ceil(file_size/p.MSS)

        self.segments[addr] = {} 
        self.ack[addr] = -1

        self.ack_events[addr] = threading.Event()

        seq_number = 0       
        with open(path, "rb") as f:     # divide o arquivo em pedacos
            chunk = f.read(p.MSS)
            
            while chunk:                              
                segment = p.make_seg(seq_number, chunk, total_segments)
                self.segments[addr][seq_number] = segment         
                seq_number += 1
                chunk = f.read(p.MSS)

        print(f"Transferencia iniciada para IP/Porta: {addr} . . .")

        self.window(total_segments, addr)


    def window(self, total_segments, addr):
        base = 0
        while base < total_segments:
            max_wnd = min(base + p.WND_SIZE, total_segments)

            for s in range(base, max_wnd):
                package = p.pack_pkt(self.segments[addr][s])
                self.socket.sendto(package, addr)

            if max_wnd == total_segments:
                break
            
            self.ack_events[addr].clear()

            ack_in_time = self.ack_events[addr].wait(timeout=0.5)
            
            if ack_in_time and self.ack[addr] >= max_wnd - 1:
                base += p.WND_SIZE
            
            else:
                print(f"   Reenvio por timeout . . .")


    # transmissao por perda/solicitacao
    def retransmit_data(self, missing_segments, addr): 
        if addr not in self.segments:
            print(f"Cliente {addr} inativo")
            return    

        print(f"Retransmitindo . . .")        
        
        for seg in missing_segments:  # procura segmento perdido no dic de segs do servidor e reenvia
            if self.segments[addr].get(seg) is not None:
                package = p.pack_pkt(self.segments[addr][seg])
                self.socket.sendto(package, addr)

            else:
                print(f"Segmento: {seg} nao foi encontrado.")
                
# instancia do servidor
if __name__ == "__main__":
    server = Server()
    server.in_listen()
   


 