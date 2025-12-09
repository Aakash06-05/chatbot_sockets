import socket,threading

DEST_IP = socket.gethostbyname(socket.gethostname())
DEST_PORT = 12345

def recieve_message(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if(message == "quit"):
                break
            print(f"{message}")
        except:
            break
    client_socket.close()

if __name__=="__main__":
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((DEST_IP,DEST_PORT))
    threading.Thread(target = recieve_message,args = (client_socket,)).start()
    while True:
        try:
            message=input(" ")
            client_socket.send(message.encode("utf-8"))
        except:
            break