import socket
import threading
import SocketServer
import time

class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
		self.wfile.write("<connect>")
		self.wfile.flush()
		self.server.addClient(self)
		self.exit_event = threading.Event()
		while self.exit_event.is_set() == False:
		    time.sleep(0.1)
		    
    def send(self, data):
        self.wfile.write(data)
        self.wfile.flush()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def __init__(self, address, handler):
        SocketServer.TCPServer.__init__(self, address, handler)
        self.clients = []
        
    def addClient(self, client):
        self.clients.append(client)
        
    def broadcast(self, data):
        for c in self.clients:
            c.send(data)

    def shutdown(self):
        for c in self.clients:
            c.exit_event.set()
        SocketServer.TCPServer.shutdown(self)

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    while True:
        response = sock.recv(1024)
        if not response: 
            break
        print "Received: " + response
    sock.close()

if __name__ == "__main__":
    import time
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name


    client_thread = threading.Thread(target=client,args=(ip,port,"Hello World"))
    client_thread.daemon = True
    client_thread.start()
	
    time.sleep(1)
    server.broadcast("xxx ")
    time.sleep(1)
    server.broadcast("yyy ")
    time.sleep(1)
    server.broadcast("zzz ")
    #client(ip, port, "Hello World 1")
    #client(ip, port, "Hello World 2")
    #client(ip, port, "Hello World 3")

    time.sleep(2)

    server.shutdown()
