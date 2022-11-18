import os
import socketserver
import threading
from unittest import *
from Server import *
import socket

class ThreadedHandler(socketserver.BaseRequestHandler): 
    def handle(self):
        data = str(self.request.recv(4096),'ascii')
        print("From Client:\n{}".format(data))
        self.request.sendall(bytes(data,'ascii'))
            
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass  
          

class ProtocolTestCase(TestCase):
    def test_clientMessageProcessing(self, data = "HELLO\nheaders: username=john;password=abc"):
        cliMsg = ChatHandler.dataToMessage(None,data)
        self.assertEqual(cliMsg.type, "HELLO")
        self.assertEqual(cliMsg.header["username"], "john")
        print(cliMsg)
    
    def test_statusMsgProcessing(self ):
        #jsonData = ChatHandler.messageToData(None,data)data = StatusMessage("HELLO","",dict({"onlineNicks": ["john","phil"]}))
        #print(jsonData)
        msg = Message(dict({"t":1}))
        print(msg["t"])   

class ServerTestCase(TestCase):            
    def test_sessionLists(self):
        s = Sessions()
        s.append(Session(id=3))
        ses = s[0]
        print(s[0].id)
        s.remove(ses)
        self.assertEqual(0,len(s.data))# should be removed

    def setUp(self):
        serverinfo = ('127.0.0.1',0)#user arbitary port
        self.server = ThreadedTCPServer(serverinfo, ThreadedHandler)
        # Start a server threaded
        serverThread = threading.Thread(target=self.server.serve_forever)
        serverThread.daemon = True
        serverThread.start()
        print("listening on {} on thread {}".format(self.server.server_address, serverThread.name))
            
    def test_clientCommunication(self, data = "HELLO\nheaders: username=john;password=abc"):  
        serverinfo = self.server.server_address
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(serverinfo)
                print("Connected to {}".format(serverinfo))
                sock.sendall(bytes(data,'ascii'))
                print("Data Sent")
                serverData = str(sock.recv(4096),'ascii')
                print("From Server: \n{}".format(serverData))
            except Exception as e:
                print(e)
            
def suite():
    suite = TestSuite()
    #suite.addTest(ClientTestCase('test_clientCommunication'))
    #suite.addTest(ServerTestCase('test_clientMessageProcessing'))
    suite.addTest(ProtocolTestCase('test_statusMsgProcessing'))
    return suite

if __name__ == '__main__':
    #main()
    runner = TextTestRunner()
    runner.run(suite())