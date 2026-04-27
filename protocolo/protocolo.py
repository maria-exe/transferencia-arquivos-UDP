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
    hr_seq = pack_data[:FORMAT]
    data = pack_data[FORMAT:]
    seg, total_seq, checksum = struct.unpack(FORMAT, hr_seq)
    
    return Segment(checksum, seg, data, total_seq)
    
# verifica o checksum
def is_corrupt(segment):
    if checksum(segment.data) == segment.checksum:
        return True
    return False

# Implementaco das mensagens de controle
# Definir claramente os formatos das mensagens de: requisição de arquivo, envio de segmento de dados 
# (incluindo cabeçalhos com número de sequência, checksum, etc.), confirmação de recebimento (se houver), 
# solicitação de retransmissão e mensagens de erro.

