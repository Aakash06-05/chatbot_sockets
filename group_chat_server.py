import socket,threading,json
import time
from datetime import datetime,timedelta
from threading import Lock

class database_server:
    def __init__(self,filename = "storage_server.json"):
        self.filename = filename
        self.lock = Lock()
        try:
            with open(self.filename,"r") as f:
                self.data = json.load(f)
        except:
            self.data = {}
    def save_message(self,message,group_id,timestamp):
        with self.lock:
            if group_id not in self.data:
                self.data[group_id]=[]
            message_format={}
            message_format["timestamp"] = timestamp
            message_format["message"] = message
            self.data[group_id].append(message_format)

            with open(self.filename,"w") as f:
                json.dump(self.data,f,indent=4)
    def get_previous_2min(self,timestamp,group_id):
        cutoff = timestamp - timedelta(minutes=2)        
        history = []
        if(group_id not in self.data):
            return []
        for instance in self.data[group_id]:
            if(datetime.strptime(instance["timestamp"], "%Y-%m-%d %H:%M:%S")>=cutoff):
                history.append(instance)
        return history


class group_manager:
    def __init__(self):
        self.groups = {}
        self.lock = Lock()
    def add_to_group(self,group_id,client_socket):
        with self.lock:
            if group_id not in self.groups:
                self.groups[group_id] = []
            self.groups[group_id].append(client_socket)
    def remove_from_group(self,group_id,client_socket):
        with self.lock:
            if group_id in self.groups:
                if client_socket in self.groups[group_id]:
                    self.groups[group_id].remove(client_socket)
    def get_clients(self,group_id):
        return self.groups.get(group_id,[])

class router:
    def __init__(self,grouping_manager):
        self.grouping_manager = grouping_manager
    def broadcast(self,message,group_id,client_socket):
        clients = self.grouping_manager.get_clients(group_id)
        for client in clients:
            if(client!=client_socket):
                final_message = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " : " + message
                client.send(final_message.encode("utf-8"))

class client_handler(threading.Thread):
    def __init__(self,client_socket,database_server,group_manager,router):
        super().__init__()
        self.client_socket = client_socket
        self.database_server = database_server
        self.group_manager = group_manager
        self.router = router
    def run(self):
        try:
            self.client_socket.send("Enter the group_id:".encode("utf-8"))
            self.group_id = self.client_socket.recv(1024).decode("utf-8")
            self.group_manager.add_to_group(self.group_id,self.client_socket)
            history = self.database_server.get_previous_2min(datetime.now(),self.group_id)
            for instance in history:
                message = "[OLD] " + instance["timestamp"] + " : " + instance["message"]
                self.client_socket.send(message.encode("utf-8"))
            while True:
                message = self.client_socket.recv(1024).decode("utf-8")
                self.router.broadcast(message,self.group_id,self.client_socket)
                self.database_server.save_message(message,self.group_id,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except:
            pass
        finally:
            self.group_manager.remove_from_group(self.group_id,self.client_socket)
            self.client_socket.close()

class connection_handler():
    def __init__(self,HOST_IP,HOST_PORT,database_server,group_manager,router):
        self.HOST_IP = HOST_IP
        self.HOST_PORT = HOST_PORT
        self.database_server = database_server
        self.group_manager = group_manager
        self.router = router
    def start(self):
        print(f"Server started...\nListening at ip{HOST_IP}")
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.bind((HOST_IP,HOST_PORT))
        server_socket.listen()

        while True:
            client_socket,client_address = server_socket.accept()
            print(f"{client_address} connected to the server")
            handle = client_handler(client_socket,self.database_server,self.group_manager,self.router)
            handle.start()

if __name__=="__main__":
    HOST_IP = socket.gethostbyname(socket.gethostname())
    HOST_PORT = 12345
    database_server = database_server()
    group_manager = group_manager()
    router = router(group_manager)
    server = connection_handler(HOST_IP,HOST_PORT,database_server,group_manager,router)
    server.start()

    