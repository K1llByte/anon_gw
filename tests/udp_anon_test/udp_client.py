import socket
import rsa
from anon_pdu import *#AnonPDU, AnonHeader, build_anon_pdu , PDU_State, PDU_Flags, PDU_Flags

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



hdr_syn = AnonHeader(PDU_State.INIT_CONNECTION,PDU_Flags.SYN)
#hdr_syn_ack_key = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.SYN | PDU_Flags.ACK,  PDU_DataOrKey.KEY)
hdr_ack_key = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.ACK,  PDU_DataOrKey.KEY)

hdr_fin = AnonHeader(PDU_State.END_CONNECTION, PDU_Flags.FIN)


pdu_syn = AnonPDU(hdr_syn)
#pdu_syn_ack_key = AnonPDU(hdr_syn_ack_key,b'server public_key')
pdu_ack_key = AnonPDU(hdr_ack_key, public_key.save_pkcs1())

pdu_fin = AnonPDU(hdr_fin)



# STARTING CONNECTION
UDPClientSocket.sendto(pdu_syn.get_bytes(), serverAddressPort)
print("SYN sent ...")

(msgFromServer ,ip_source) = UDPClientSocket.recvfrom(bufferSize)
print("SYN,ACK,KEY received ...",ip_source)

his_public_key = rsa.PublicKey.load_pkcs1(build_anon_pdu(msgFromServer).get_payload())
UDPClientSocket.sendto(pdu_ack_key.get_bytes(), serverAddressPort)
print("ACK,KEY sent!")

#####################
# TODO: data exchange
#####################

# ENDING CONNECTION
UDPClientSocket.sendto(rsa.encrypt(pdu_fin.get_bytes(),his_public_key), serverAddressPort)
print("encrypted FIN sent!")

(msgFromServer ,ip_source) = UDPClientSocket.recvfrom(bufferSize)
print("encrypted ACK received ...",ip_source)

print("Encrypted fin ack:",build_anon_pdu(msgFromServer))
print()
print("Decrypted fin ack:",build_anon_pdu(rsa.decrypt(msgFromServer,private_key)))


#print("encrypted:",msgFromServer)
#print()
#print("decrypted:",rsa.decrypt(msgFromServer,private_key))