import socket
import rsa

(public_key,private_key) = rsa.newkeys(1024,poolsize=4)

#print(public_key)
#print("")
#print(public_key.save_pkcs1())

#public_key.save_pkcs1()
#print(private_key)

#unknown_key = rsa.PublicKey.load_pkcs1(msg)


#######################################################


msgFromClient = public_key.save_pkcs1()
#keyFromCLient = public_key.save_pkcs1()

#syn_toSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

 

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# Send to server using created UDP socket

UDPClientSocket.sendto(msgFromClient, serverAddressPort)
print("Public key sent ...")


(msgFromServer ,ip_source) = UDPClientSocket.recvfrom(bufferSize)
print("Received response!:",ip_source)

print("encrypted:",msgFromServer)
print()
print("decrypted:",rsa.decrypt(msgFromServer,private_key))


#
#for i in range(5):
#    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
#    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
#    msg = "Message from Server {}".format(msgFromServer[0])
#    print(msg)