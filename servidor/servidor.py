import socket as s

class Server:
    def __init__(self):
        pass

    def reception():
        serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        serverSocket.bind(('', 12000))

        print('Escutando...')

        while True:
            msg, addr = serverSocket.recvfrom(2048)
            print(f"Recebi de {addr}: {msg.decode()}")
            mod_msg = msg.decode().upper()
            serverSocket.sendto(mod_msg.encode(), addr)

    def request_file_process():
        pass

    def file_transmission():
        pass


 