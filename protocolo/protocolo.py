# protocolo de transferência confiável de dados
# 1. sem dados corrompidos, 2. perdidos e 3. fora de ordem

# 1. Detecção de erro (checksum) -- protocolo

# 2. Ordenação (n de sequencia) -- no dataclass segmento
 
# 3. Retransmissão --- na classe servidor

from dataclasses import dataclass
import struct, zlib

MAX_DGRAM = 1472
PORT = 12000
FORMAT = "!I I I"

# estrutura do pacote de dados
@dataclass
class Segment: 
    checksum: int
    seg: int    # dps precisa checar esse número para determinar se é retransmissão
    data: bytes
    total_seg: int

def checksum(data):
    return zlib.crc32(data)

# cria o segmento
def make_pkt(seg, data, total_seg):
    checksum = checksum(data)
    return Segment(checksum, seg, data, total_seg)

def extract_pkt(packet, data):
    pass

def verify_seq_number():
    pass
# funcoes do protocolo de aplicacao



# 0 nak, 1 ack