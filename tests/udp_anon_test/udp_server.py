import socket
import rsa
from queue import Queue
from conn_queue import ConnectionWaiting
from conn_table import ConnectionTable
from anon_pdu import *
import threading
 
#q = Queue(2)
######################## META DATA ########################
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

cw = ConnectionWaiting()
ct = ConnectionTable()

(public_key,private_key) = rsa.newkeys(1024,poolsize=4)
###########################################################

localIP     = "0.0.0.0"
localPort   = 20001
bufferSize  = 1024



#msgFromServer       = "Hello UDP Client"

#bytesToSend         = str.encode(msgFromServer)

 
# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))



class UDP_Receiver(threading.Thread):
    def __init__(self, tuple_ip_port, his_public_key):
        threading.Thread.__init__(self)
        self.tuple_ip_port = tuple_ip_port
        self.his_public_key = his_public_key

    def run(self):
        end_conn = False
        while(not end_conn):
            # All pdu's received in this thread are encrypted!
            pdu = build_anon_pdu(rsa.decrypt(ct.dequeue(self.tuple_ip_port),private_key)) # Message decrypt
            hdr = pdu.get_header()

            # Check if header is to end connection
            if hdr.state == PDU_State.END_CONNECTION and hdr.flags == PDU_Flags.FIN:
                hdr_ack = AnonHeader(PDU_State.END_CONNECTION, PDU_Flags.ACK)
                pdu_ack = AnonPDU(hdr_ack)

                UDPServerSocket.sendto(rsa.encrypt(pdu_ack.get_bytes(), self.his_public_key), self.tuple_ip_port) # Message encrypt

                ct.remove(self.tuple_ip_port)
                end_conn = True
            
            elif hdr.state == PDU_State.DATA_EXCHANGE and hdr.data_or_key == PDU_DataOrKey.DATA:
                hdr_ack = AnonHeader(PDU_State.DATA_EXCHANGE, PDU_Flags.ACK)
                pdu_ack = AnonPDU(hdr_ack)

                UDPServerSocket.sendto(rsa.encrypt(pdu_ack.get_bytes(), self.his_public_key), self.tuple_ip_port) # Message encrypt

 
def handle_pdu(raw_pdu,tuple_ip_port):

    if ct.contains(tuple_ip_port):
        ct.enqueue(tuple_ip_port,raw_pdu)
        # Corresponding threads will send the response

    else:
        pdu = build_anon_pdu(raw_pdu)
        pdu_header = pdu.get_header()
        if pdu_header.state == PDU_State.INIT_CONNECTION:

            if cw.contains(tuple_ip_port):
                if (pdu_header.flags & PDU_Flags.ACK) and (pdu_header.data_or_key & PDU_DataOrKey.KEY):
                    if cw.remove(tuple_ip_port): # TODO: put this in the if above

                        his_public_key = rsa.PublicKey.load_pkcs1(pdu.get_payload()) #The payload here is his public_key in PEM format
                        ct.add(tuple_ip_port, his_public_key) 

                        UDP_Receiver(tuple_ip_port,his_public_key).start()
            else:
                if (pdu_header.flags & PDU_Flags.SYN):
                    if cw.add(tuple_ip_port): # TODO: put this in the if above
                        print("Added to Waiting connection table")
                        hdr_syn_ack_key = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.SYN | PDU_Flags.ACK,  PDU_DataOrKey.KEY)
                        pdu_syn_ack_key = AnonPDU(hdr_syn_ack_key, public_key.save_pkcs1())

                        UDPServerSocket.sendto(pdu_syn_ack_key.get_bytes(), tuple_ip_port)


print("UDP server up and listening")

# Listen for incoming datagrams
asd = 0
while(True):    
    bytes_address = UDPServerSocket.recvfrom(bufferSize)
    message = bytes_address[0]
    tuple_ip_port = bytes_address[1]

    handle_pdu(message,tuple_ip_port)
    
    #print("Message from Client: {}".format(message))
    #print("Client IP Address: {}:{}".format(tuple_ip_port[0],tuple_ip_port[1]))
    
    #asd += 1
    if asd > 3:
        break

print("exited server")

print(ct)

