# Server
import collections
import socketserver
import socket
from dataclasses import dataclass, field, asdict
import threading
import json
from enum import Enum

@dataclass
class Session:
    id: str = ""
    userid : str = ""
    expires: str = ""
    connectted_time: str = ""
    lastinteraction_time: str = ""
    ip: str = ""
    conn_thread: str = ""

@dataclass
class User:
     id: str = ""
     name: str= ""
     password: str = ""
 
 
class Sessions():
    data : list = []
    
    def findByUserId(self, id) -> Session:
        for session in self.data:
            if session.userid == id:
                return session
            else: return None 
    
    def findById(self, id) -> Session:
        for session in self.data:
            if session.id == id:
                return session
            else: return None 
    
    def __getitem__(self,i) -> Session:
        return self.data[i]
    
    def __setitem__(self,i, data:Session):
        self.data[i] = data
        
    def append(self,data:Session):
        self.data.append(data)
    
    def remove(self, data:Session):
        self.data.remove(data)

class Users():
    data : list = []
    
    def findByName(self, name) -> User:
        for u in self.data:
            if u.name == name:
                return u
            else: return None 
    
    def findById(self, id) -> User:
        for u in self.data:
            if u.id == id:
                return u
            else: return None 
    
    def __getitem__(self,i) -> User:
        return self.data[i]
    
    def __setitem__(self,i, data:User):
        self.data[i] = data
        
    def append(self,data:User):
        self.data.append(data)
    
    def remove(self, data:User):
        self.data.remove(data)            
    

@dataclass
class Message(dict):
    type = "" # Type of message;
    message: str = "" # base64 of message if any
    
    class Types(Enum):
        HELLO = "HELLO"
        MESSAGE = "MESSAGE"
        BYE = "BYE"
        PING = "PING"

    def __init__(self,data):
        super().__init__(data)
    
    def toJSON(self):
        return asdict(self)
    
    def decode(data):
        lines = data.split('\n')
        type = lines[0]
        data = json.loads(lines[1]) 
        
        if Message.Types[type] in Message.Types:   
            return Message(data)
    
    def encode(self) -> str:
        encString:str = ""
        encString += "{}\n".format(self.type)
        #encString += "message: {}\n".format(msg.message)# TODO: encode to base64
        encString += "{}\n".format(self.toJSON())
        encString += "\n"
        return encString

@dataclass
class MailMessage(Message):
    header: dict = field(default_factory=dict) # Headers related to message/status
    sender: str= ""# id of sender
    recipient: str = ""# id of recip if any
    attachment = None # base64 of any attachment 
@dataclass
class StatusMessage(Message):
    class Status(Enum):
        INFO = 1
        ERROR = 2
        WARN = 3

    
    data: dict = field(default_factory=dict)
    status = Status.INFO
@dataclass
class ServerStatusMessage(StatusMessage):
    online: list = field(default_factory=list)# list of tuples of nick/nickID pairs
@dataclass
class ClientStatusMessage(StatusMessage):
    pass


messageTypes = ["HELLO","MESSAGE","BYE","PING"]

class ChatHandler(socketserver.BaseRequestHandler):
    clientInfo = dict()
    sessions = Sessions()
    messageQueue = dict()# key is id of recipient 
    users = Users()
    
    def getOnlineUsers(self) -> list:
        l : list
        for s in self.sessions:
             l.append((self.users.findById(s.userid).name, s.userid))
        return l
    
    def handle(self):
        # Recieve data from cli and proces message
        with self.request.recv(4096) as self.data:
            self.data = str(self.data,'ascii')
            with self.dataToMessage(self.data) as cliMsg:
                userid = self.users.findByName((cliMsg.header['username']))
                session = self.sessions.findByUserId(userid) 
                
                if cliMsg.type == "HELLO" and session == None:# if handshake from new cli Register new connection / session
                    #TODO: chnage sessid to uuid
                    id = '0'
                    self.sessions.append(Session(id=id, username=cliMsg.header['username'], ip=self.client_address[0] ))
                    # send Ok to client with userID of user list of online people/IDs
                    self.sens.sendall(ServerStatusMessage("HELLO",online = self.getOnlineUsers()))
                if session == None:
                    #error
                    pass
                if cliMsg.type == "MESSAGE":
                    # Store message in queue
                    if self.sessions.findByUserId(cliMsg.recipient) == None:
                        # TODO: recip not logged on - send reponse 
                        pass
                    else:
                        # Add message to que
                        if cliMsg.recipient in self.messageQueue.keys():
                            if type(self.messageQueue[cliMsg.recipient]) == list:
                                self.messageQueue[cliMsg.recipient].append(cliMsg)
                        else:
                            self.messageQueue[cliMsg.recipient] = [cliMsg]
                        
                        
                elif cliMsg.type == "BYE":
                    pass # TODO: Logout session
                elif cliMsg.type == "PING":
                    pass # TODO: Check for messages and send
                    

    def dataToMessage(self, data) -> Message:
        type = ""
        header= dict()
        lines = data.split('\n')
        for line in lines:
            if line in messageTypes:
                type = line
            if "headers: " in line:
                headers = line.split(": ")[1].split(";")
                for h in headers:
                    key,value = h.split('=')
                    header[key] = value
            if "data: " in line:
                headers = json.loads(line.split(": ")[1])
       
        return Message(type,header,"","")
    
    def messageToData(self, msg:Message) -> str:
        encString:str = ""
        encString += "{}\n".format(msg.type)
        #encString += "message: {}\n".format(msg.message)# TODO: encode to base64
        encString += "{}\n".format(msg.toJSON())
        encString += "\n"
        return encString
        
    # Send formulated message to recipent
    def send(self, message:Message):
        if message.recipient != "":
            # get recipient conn. info
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect()
            
            # connectiion loop
            while True:
                # Connect to server with connection info
                if name == "":
                    name = input('Enter your name: ')
                    sock.sendall(bytes("username: "+name,'utf-8'))
                    # Wait for response
                    data = sock.recv(4096)
                
                
                print(data)
                # input text
                message = input('=> ')
                sock.sendall(bytes(message))
        self.request.sendall(bytes(data,'ascii'))
    
    
    
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass   


def ChatClient(clientinfo= ('127.0.0.1',1234), name = ""):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # try to conn to server on port
        try:
            sock.connect(self.address)
        except:
            print('An exception occurred')
        
        # connectiion loop
        while True:
            # Connect to server with connection info
            if name == "":
                name = input('Enter your name: ')
                sock.sendall(bytes("username: "+name,'utf-8'))
                # Wait for response
                data = sock.recv(4096)
            print(data)
            # input text
            message = input('=> ')
            sock.sendall(bytes(message))


if __name__ == "__main__" :
    serverinfo = ('127.0.0.1',0)#user arbitary port
    server = ThreadedTCPServer(serverinfo, ChatHandler)
    # Start a server threaded
    serverThread = threading.Thread(target=server.serve_forever)
    serverThread.daemon = True
    serverThread.start()
    print("listening on {} on thread {}".format(server.server_address, serverThread.name))