import socket
import threading

#HEADERS
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 12345
PACKET_SIZE = 1024
ENCODER = "utf-8"

clients=[]
Usernames=[]

def broadcast(message):
    for client in clients:
        client.send(message.encode(ENCODER))
def recieve(client_socket):
    while True:
        try:
            message = client_socket.recv(PACKET_SIZE).decode(ENCODER)
            index = clients.index(client_socket)
            broadcast(f"{Usernames[index]}: {message}")
        except:
            index = clients.index(client_socket)
            clients.remove(client_socket)
            broadcast(f"{Usernames[index]} has left the channel")
            Usernames.remove(Usernames[index])
            client_socket.close()
            break

def main():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((HOST_IP,HOST_PORT))
    server_socket.listen()
    print(f"Listening in ip : {HOST_IP}")
    while True:
        client_socket,client_addr = server_socket.accept()
        client_socket.send("Username:".encode(ENCODER))
        Username = client_socket.recv(PACKET_SIZE).decode(ENCODER)
        clients.append(client_socket)
        broadcast(f"{Username} has entered the chat")
        Usernames.append(Username)
        thread = threading.Thread(target=recieve,args=(client_socket,))
        thread.start()
    server_socket.close()
main()


