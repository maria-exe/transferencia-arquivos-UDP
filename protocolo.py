from dataclasses import dataclass
import struct, zlib


MAX_DGRAM = 1472
PORT = 2000
FORMAT = "!I I I"

HEADER = struct.calcsize(FORMAT)
MSS = MAX_DGRAM - HEADER
TIMEOUT = 2
WND_SIZE = 300

# estrutura do pacote de dados
@dataclass
class Segment: 
    seg: int
    checksum: int
    total_seg: int
    data: bytes

def checksum(data):
    return zlib.crc32(data)

def make_seg(seg, data, total_seg):
    csum = checksum(data)
    return Segment(seg, csum, total_seg, data)

# empacota segmento
def pack_pkt(segment):
    header = struct.pack (
        FORMAT, 
        segment.seg,
        segment.total_seg,
        segment.checksum
    )
    return header + segment.data

def unpack_pkt(pack_data):
    seg, total_seq, csum = struct.unpack_from(FORMAT, pack_data)
    data = pack_data[HEADER:]
    
    return Segment(seg, csum, total_seq, data)

def is_corrupt(segment):
    if checksum(segment.data) == segment.checksum:
        return False
    return True

def get(request_file): # requisicao de arquivos
    return f"GET/{request_file}".encode()

def error(request_file): # mensagens de erro
    return f"ERR/Arquivo {request_file} nao encontrado".encode()

def retrans_request(segments): # solicitacao de retransmissao
    str_seg = ':'.join(map(str, segments))
    return f"RTS/{str_seg}".encode()

def ack(seq_num):
    return f"ACK/{seq_num}".encode()

def decode_message(bytes_msg): # decodifica os bytes e identifica o tipo de mensagem de controle
    if bytes_msg.startswith(b"GET"):
        return "GET", bytes_msg.decode().split("/", 1)[1]
    
    elif bytes_msg.startswith(b"ERR"):
        return "ERR", bytes_msg.decode().split("/", 1)[1]
    
    elif bytes_msg.startswith(b"RTS"):
        msg = bytes_msg.decode().split("/", 1)[1] 
        segments = []
        if msg:
            for s in msg.split(":"):
                segments.append(int(s))
        return "RTS", segments
    
    elif bytes_msg.startswith(b"ACK"):
        seg = int(bytes_msg.decode().split("/", 1)[1])
        return "ACK", seg

    return "DATA", None
    


