import os, sys, socket as s, threading, math

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

    # verifica se o arquivo existe
    def _verify_request_file(self, file_name):
        path = os.path.join(os.path.dirname(__file__), 'files', file_name)
        return os.path.exists(path) and os.path.isfile(path)
    
    # divisao de arquivos em chuncks - MTU
    def send_file(self, file_name, addr):
        path = os.path.join(os.path.dirname(__file__), 'files', file_name)

        file_size = os.path.getsize(path)
        total_segments = math.ceil(file_size/p.MSS)

        self.segments[addr] = {} 
        self.ack[addr] = -1

        self.ack_events[addr] = threading.Event()

        seq_num = 0       

        with open(path, "rb") as f:
            chunk = f.read(p.MSS)
            while chunk:                              
                segment = p.make_seg(seq_num, chunk, total_segments)
                self.segments[addr][seq_num] = segment         
                seq_num += 1
                chunk = f.read(p.MSS)

        print("Transferencia iniciada . . .")
        # python cliente.py @127.0.0.1:2000/teste2.pdf
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
            
            if ack_in_time and self.ack.get(addr, -1) >= max_wnd - 1:
                base += p.WND_SIZE
            
            else:
                print(f"Reenvio por timeout . . .")

     
    def handle_request(self, data, addr):
        request_type, decoded_data = p.decode_message(data)

        if request_type == "GET": 
            if self._verify_request_file(decoded_data):# se o arquivo existe
                self.send_file(decoded_data, addr)
                
            else: 
                self.send_error(decoded_data, addr)
        
        elif request_type == "RTS":
            self.retransmit_data(decoded_data, addr)

        elif request_type == "ACK":
            self.ack[addr] = decoded_data
            if addr in self.ack_events:
                self.ack_events[addr].set()

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
            print(f"Nenhuma sessao ativa para {addr}")
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
   


 