import socket
import rsa
from queue import Queue
 
#q = Queue(2)

connection_table = {}

approved =  [ "127.0.0.1" ]

for ip in approved:
    connection_table[ip] = {}

#connection_table["127.0.0.1"]["423"] = Queue(5)

#def print_connection_table(ct):
#    for ip in ct:
#        print(ip,":")
#        for port in ct[ip]:
#            print("  ",port,":")
#            print("  ",ct[ip][port].maxsize)

print(connection_table)
#del connection_table["127.0.0.1"]
#print(connection_table)


localIP     = "0.0.0.0"

localPort   = 20001

bufferSize  = 1024

 

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)

 

# Create a datagram socket

soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

 

# Bind to address and ip

soc.bind((localIP, localPort))

soc.listen(1)

print("TCP server up and listening")


# Listening
while(True):
    (conn, addr) = soc.accept()
    message = conn.recv(bufferSize)

    print("Message from {}: {}".format(addr,message))

    # Sending a reply to client
    conn.sendall(b"Ola cliente!")

    conn.close()
print("exited server")

print(connection_table)