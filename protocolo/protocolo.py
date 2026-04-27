from dataclasses import dataclass
import struct, zlib

MAX_DGRAM = 1472
PORT = 5000
FORMAT = "!I I I"
H_SIZE = struct.calcsize(FORMAT)  
PAYLOAD_SIZE = MAX_DGRAM - H_SIZE

# estrutura do pacote de dados
@dataclass
class Segment: 
    checksum: int
    seg: int    
    data: bytes
    total_seg: int

def checksum(data):
    return zlib.crc32(data)

# cria o segmento
def make_pkt(seg, data, total_seg):
    csum = checksum(data)
    return Segment(csum, seg, data, total_seg)

# transforma o segmento em bytes (empacota)
def pack_pkt(segment):
    hr_seq = struct.pack(
        FORMAT,
        segment.seg,
        segment.total_seg,
        segment.checksum
    )
    return hr_seq + segment.data

# desempacota o segmento
def extract_pkt(pack_data):
    hr_seq = pack_data[:H_SIZE]
    data = pack_data[H_SIZE:]
    seg, total_seq, checksum = struct.unpack(FORMAT, hr_seq)
    
    return Segment(checksum, seg, data, total_seq)
    
# verifica o checksum
def is_corrupt(segment):
    if checksum(segment.data) == segment.checksum:
        return False
    return True

def get(request_file): # requisicao de arquivos
    return f"GTT:{request_file}".encode()

def error(request_file): # mensagens de erro
    return f"ERR:{request_file}".encode()

def retrans_request(segments): # solicitacao de retransmissao
    str_seg = ':'.join(map(str, segments))
    return f"RTS:{str_seg}".encode()

def decode_message(bytes_msg): # decodifica os bytes e identifica o tipo de mensagem de controle
    if bytes_msg.startswith(b"GTT"):
        return "GET", bytes_msg.decode().split(":", 1)[1]
    
    elif bytes_msg.startswith(b"ERR"):
        return "ERR", bytes_msg.decode().split(":", 1)[1]
    
    elif bytes_msg.startswith(b"RTS"):
        
        msg = bytes_msg.decode().split(":", 1)[1]
        
        segments = []
        for s in msg.split(":"):
            segments.append(int(s))
        
        return "RTS", segments
    
    return "DATA", None
    


