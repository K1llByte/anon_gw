import socket


serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

 

# Create a UDP socket at client side

soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

soc.connect(serverAddressPort)

# Send to server using created UDP socket

soc.sendall(b"Ola servidor...")
print("Message sent ...")

message, addr = soc.recvfrom(bufferSize)
print("Message from {}:{}".format(addr,message))


#
#for i in range(5):
#    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
#    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
#    msg = "Message from Server {}".format(msgFromServer[0])
#    print(msg)