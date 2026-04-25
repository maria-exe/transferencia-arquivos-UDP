import socket as s

    # class Protocol: 
    #     pass

    # class RequestProcess: 
    #     pass

    # class FileTransmission: 
    #     pass

serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
serverSocket.bind(('', 12000))

print('Escutando...')

while True:
    msg, addr = serverSocket.recvfrom(2048)
    print(f"Recebi de {addr}: {msg.decode()}")
    mod_msg = msg.decode().upper()
    serverSocket.sendto(mod_msg.encode(), addr)


 