import socket as s
import os, sys, random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import protocolo as p

LOSS_SIMUL = False
LOSS_RATE = 0.01

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

    def send_request(self, ip, port, file_name): # GET
        addr = (ip, port)
        message = p.get(file_name)
        
        self.socket.sendto(message, (ip, port))
        
        self.receive_segments()

        retries = 0
        max_retries = 3

        while self.missing_segments() and retries < max_retries:
            last_missing = len(self.missing_segments())
            
            self.request_retransmit(addr)
            self.receive_segments()

            if len(self.missing_segments()) == last_missing:
                retries += 1
                print(f"Falha na retransmissao")
            else:
                retries = 0 
            
        if self.missing_segments():
            print("Arquivo incompleto.")
            sys.exit(1)

        data = self.mount_segment()
        self.save_file(file_name, data)

        
    def receive_segments(self):
        self.socket.settimeout(p.TIMEOUT)
        while True: 
            try:
                recv_seg, addr = self.socket.recvfrom(p.MAX_DGRAM)
                msg_type, data = p.decode_message(recv_seg)

                if msg_type == "ERR":
                    print(f"Erro retornado pelo servidor: {data}")
                    sys.exit(1)

                elif msg_type == "DATA":
                    dmount_seg = p.unpack_pkt(recv_seg)

                    if not p.is_corrupt(dmount_seg):

                        if LOSS_SIMUL and random.random() < LOSS_RATE:
                            print(f"\nSegmento {dmount_seg.seg} descartado.")

                        self.segments[dmount_seg.seg] = dmount_seg
                        self.total_segments = dmount_seg.total_seg

                        file_end = dmount_seg.seg >= self.total_segments - 1
                        wnd_end = (dmount_seg.seg + 1) % p.WND_SIZE == 0

                        if file_end or wnd_end:
                            ack_msg = p.ack(dmount_seg.seg)
                            self.socket.sendto(ack_msg, addr)
                            
            except s.timeout:
                break
        
    def mount_segment(self):
        print("Remotando arquivo.")
        file_data = b"" # tipo obj de bytes
        
        data = [self.segments[seq].data for seq in sorted(self.segments.keys())]
        file_data = b"".join(data)
        
        print(f"Arquivo remontado.")
        return file_data

    # verifica se foi recebido todos os segmentos
    def missing_segments(self):
        if self.total_segments is None:
            return []
        
        expect_segments = set(range(self.total_segments))
        received_segments = set(self.segments.keys())
        missing_segs = expect_segments - received_segments
        
        return list(missing_segs)

    def save_file(self, file_name, mount_data):
        folder = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(folder, exist_ok=True)
        full_path = os.path.join(folder, file_name)

        try:
            with open(full_path, "wb") as f:
                f.write(mount_data)
            
            print("Arquivo salvo")
            
            os.system(f"xdg-open {full_path}")  
        
        except OSError as e:
            print(f"Erro ao salvar arquivo: {e}")

    # solicitar retransmissão de arquivos
    def request_retransmit(self, addr):
        missing = self.missing_segments()
        print(f"Solicitando retransmissao . . .")

        chunk_size = 100
        for i in range(0, len(missing), chunk_size):
            lote = missing[i : i + chunk_size]
            message = p.retrans_request(lote)
            self.socket.sendto(message, addr)

if __name__ == "__main__":
    ip, porta, filename = file_parser()
    client = Client()
    
    try:
        client.send_request(ip, porta, filename)
    
    except s.timeout:
        print("Erro: servidor não encontrado")
    
    finally:
        client.socket.close()
        print("Comunicacao Encerrada :)")