import socket as s


request = input("Digite o destino: ")
path, file = request.strip('@').split('/')
ip_address, port = path.split(':')
        
clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)

message = "Hello World!"
clientSocket.sendto(message.encode(), (ip_address, int(port)))

resp, addr = clientSocket.recvfrom(2048)

print('Servidor:', resp.decode())
clientSocket.close()


