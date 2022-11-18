# Client
import socket

address= ('127.0.0.1',1234)
name = ""
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # try to conn to server on port
    try:
      sock.connect(address)
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

   
    sock.close()