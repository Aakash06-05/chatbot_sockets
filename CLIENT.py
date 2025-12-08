import socket
import threading

#HEADER
DEST_IP = socket.gethostbyname(socket.gethostname())
DEST_PORT = 12345
ENCODER = "utf-8"
PACKET_SIZE = 1024

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def send_message(client_socket):
    while True:
        message = input("")
        client_socket.send(message.encode(ENCODER))
def recieve_message(client_socket):
    while True:
        try:
            message = client_socket.recv(PACKET_SIZE).decode(ENCODER)
            if(message == "Username:"):
                nickname = input("Enter the username:")
                client_socket.send(nickname.encode(ENCODER))
            else:
                print(f"{message}")
        except:
            print("Error occured")
            client_socket.close()
            break


def main():
    client_socket.connect((DEST_IP,DEST_PORT))
    thread1 = threading.Thread(target= send_message,args = (client_socket, ))
    thread2 = threading.Thread(target= recieve_message,args = (client_socket, ))
    thread2.start()
    thread1.start()
main()