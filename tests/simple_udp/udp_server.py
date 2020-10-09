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

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 
# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

 
print("UDP server up and listening")
 

# Listen for incoming datagrams
asd = 0
while(True):    
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address,port = bytesAddressPair[1]

    #if connection_table[address] == None:
    #    print(address,"not found on table")
    
    #connection_table[address][port] = Queue(5)

    print("Message from Client:{}".format(message))
    print("Client IP Address:{}:{}".format(address,port))

    his_public_key = rsa.PublicKey.load_pkcs1(message)

    # Sending a reply to client
    UDPServerSocket.sendto(rsa.encrypt(b"ola mundo",his_public_key), (address,port))

    asd += 1

print("exited server")

print(connection_table)