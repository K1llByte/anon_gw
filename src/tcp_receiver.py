import socket
import threading
import random
from anon_pdu import *
#from shared_data import *
from shared_data import BUFFER_SIZE, TCP_PORT, UDP_PORT, TIMEOUT_MILLIS, IP, public_key, private_key, udp_socket, conection_wait, conection_table, Id , HEADER_SIZE, UDP_BUFFER_SIZE
import os
from utils import aes
from utils import unix_time_millis
import datetime



######################################## UDP RECEIVER ########################################

class UDP_Read_TCP_Write(threading.Thread):
    
    
    def __init__(self, tuple_ip_id, aes_key, conn):
        threading.Thread.__init__(self)
        self.tuple_ip_id = tuple_ip_id
        self.aes_key = aes_key
        self.conn = conn

    def run(self):
        tuple_ip_port = (self.tuple_ip_id[0],UDP_PORT)
        end_conn = False
        while(conection_table.write_is_open(self.tuple_ip_id)): #
            # All pdu's received in this thread are encrypted!
            pdu = conection_table.dequeue(self.tuple_ip_id) # Message decrypt
            pdu.decrypt(self.aes_key)
            hdr = pdu.get_header()
            print(pdu)

            # Check if header is to end connection
            if hdr.state == PDU_State.END_CONNECTION and hdr.flags == PDU_Flags.FIN:
                hdr_ack = AnonHeader(PDU_State.END_CONNECTION, PDU_Flags.ACK, id=self.tuple_ip_id[1])
                pdu_ack = AnonPDU(hdr_ack)
                pdu_ack.encrypt(self.aes_key) # Message encrypt
                
                udp_socket.sendto(pdu_ack.get_bytes(), tuple_ip_port)

                if conection_table.close_write(self.tuple_ip_id) == 1:
                    conection_table.remove(self.tuple_ip_id)
                self.conn.close()
                print("I Closed Socket TCP")
                #print("conection_table:",conection_table)
                #print("conection_wait:",conection_wait)

            elif hdr.state == PDU_State.END_CONNECTION and hdr.flags == PDU_Flags.ACK:
                #if conection_table.close_read(self.tuple_ip_id) == 1:
                #    conection_table.remove(self.tuple_ip_id)
                
                #conection_table.unverified_get(self.tuple_ip_id)
                print("He closed Socket TCP")
            
            elif hdr.state == PDU_State.DATA_EXCHANGE and hdr.flags == PDU_Flags.ACK:
                #print("===== I should ack the prev packet next")
                conection_table.unverified_get(self.tuple_ip_id)
                
            elif hdr.state == PDU_State.DATA_EXCHANGE and hdr.data_or_key == PDU_DataOrKey.DATA:
                hdr_ack = AnonHeader(PDU_State.DATA_EXCHANGE, PDU_Flags.ACK, id=self.tuple_ip_id[1])
                pdu_ack = AnonPDU(hdr_ack)
                pdu_ack.encrypt(self.aes_key) # Message encrypt
                udp_socket.sendto(pdu_ack.get_bytes(), tuple_ip_port)
                
                # TODO: Send ack through a new queue to comunicate between UDP_Read and USP_Write threads
                self.conn.send(pdu.get_payload())
                print("Sent to target")
        print("UDP_Read_TCP_Write End")
        #print("conection_table:",conection_table)
        #print("conection_wait:",conection_wait)



class UDP_Receiver(threading.Thread):

    
    def __init__(self,ip_port_peers):
        threading.Thread.__init__(self)
        self.TARGET_IP = ip_port_peers[0]
        self.TARGET_PORT = ip_port_peers[1]
        self.overlay_peers = ip_port_peers[2]

    def run(self):
        print("UDP Server Opened at: {}:{}".format(IP, UDP_PORT))
        while(True):    
            bytes_address = udp_socket.recvfrom(UDP_BUFFER_SIZE)
            raw_pdu = bytes_address[0]
            
            tuple_ip_port = bytes_address[1]

            pdu = build_anon_pdu(raw_pdu)
            pdu_header = pdu.get_header()

            print(">",tuple_ip_port,"UDP Received","ID:",pdu_header.id)
            # PDU Handler related
            tuple_ip_id = (tuple_ip_port[0], pdu_header.id)
            

            if conection_table.contains(tuple_ip_id):
                # Corresponding threads will send the response
                conection_table.enqueue(tuple_ip_id,pdu)

            else:
                if pdu_header.state == PDU_State.INIT_CONNECTION:
                    handshake_state = conection_wait.get(tuple_ip_id)
                    if handshake_state == 2:
                        if (pdu_header.flags & PDU_Flags.ACK) and (pdu_header.data_or_key & PDU_DataOrKey.KEY):
                            if conection_wait.remove(tuple_ip_id): # TODO: put this in the if above
                            
                                aes_key = rsa.decrypt(pdu.get_payload(),private_key) #The payload here is a aes_key encrypted with rsa public key
                                if conection_table.add(tuple_ip_id, aes_key):

                                    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
                                    soc.connect((self.TARGET_IP,self.TARGET_PORT))
                                    UDP_Read_TCP_Write(tuple_ip_id, aes_key, soc).start()
                                    TCP_Read_UDP_Write(tuple_ip_id, aes_key, soc).start()
                                    print("= CONNECTION STABLISHED Peer2 =")

                    elif handshake_state == 1:
                        if (pdu_header.flags & PDU_Flags.SYN) and (pdu_header.flags & PDU_Flags.ACK) and (pdu_header.data_or_key & PDU_DataOrKey.P_KEY):
                            client_soc = conection_wait.get_client_soc(tuple_ip_id)
                            if conection_wait.remove(tuple_ip_id): 

                                his_public_key = rsa.PublicKey.load_pkcs1(pdu.get_payload())
                                aes_key = os.urandom(32) 
                                if conection_table.add(tuple_ip_id, aes_key):

                                    hdr_ack = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.ACK,  PDU_DataOrKey.KEY, id=tuple_ip_id[1])
                                    pdu_ack = AnonPDU(hdr_ack, rsa.encrypt(aes_key ,his_public_key))

                                    udp_socket.sendto(pdu_ack.get_bytes(), tuple_ip_port)
                                    print("ACK,KEY sent ...")

                                    print("= CONNECTION STABLISHED Peer1 =")
                                    
                                    UDP_Read_TCP_Write(tuple_ip_id, aes_key, client_soc).start()
                                    TCP_Read_UDP_Write(tuple_ip_id, aes_key, client_soc).start()
                                    
                    else:
                        if (pdu_header.flags & PDU_Flags.SYN):
                            if conection_wait.add(tuple_ip_id,2): # TODO: put this in the if above

                                # Constructs header and pdu for reply
                                hdr_syn_ack_key = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.SYN | PDU_Flags.ACK,  PDU_DataOrKey.P_KEY, id=tuple_ip_id[1])
                                pdu_syn_ack_key = AnonPDU(hdr_syn_ack_key, public_key.save_pkcs1())

                                udp_socket.sendto(pdu_syn_ack_key.get_bytes(), tuple_ip_port)
                                print("SYN,ACK,KEY sent ...")

            #handle_pdu(message,(tuple_ip_port[0], self.self.next_id))


######################################## TCP RECEIVER ########################################

class TCP_Read_UDP_Write(threading.Thread):


    def __init__(self, tuple_ip_id, aes_key, conn):
        threading.Thread.__init__(self)
        self.tuple_ip_id = tuple_ip_id
        self.aes_key = aes_key
        self.conn = conn

    def run(self):

        tuple_ip_port = (self.tuple_ip_id[0], UDP_PORT)

        while(conection_table.read_is_open(self.tuple_ip_id)):
            message = self.conn.recv(BUFFER_SIZE - HEADER_SIZE)
            print("> TCP Received:",message)
            if not message:
                pdu_fin = AnonPDU(AnonHeader(PDU_State.END_CONNECTION, PDU_Flags.FIN, id=self.tuple_ip_id[1]))
                pdu_fin.encrypt(self.aes_key)
                print("    > Sent FIN")
                #self.conn.close()
                conection_table.unverified_put(self.tuple_ip_id, pdu_fin)
                udp_socket.sendto(pdu_fin.get_bytes(), tuple_ip_port)
                

                # Wait for ack process
                #begin = unix_time_millis(datetime.datetime.now())
                #while True:
                #    if conection_table.unverified_empty(self.tuple_ip_id):
                #        # If is empty then the packet received ack in the udp read thread
                #        break
#
                #    end = unix_time_millis(datetime.datetime.now())
                #    if end - begin >= TIMEOUT_MILLIS:
                #        begin = unix_time_millis(datetime.datetime.now())
                #        print("    > Resent FIN")
                #        udp_socket.sendto(pdu_fin.get_bytes(), tuple_ip_port)
#
                if conection_table.close_read(self.tuple_ip_id) == 1:
                    conection_table.remove(self.tuple_ip_id)

            else:
                pdu_msg = AnonPDU(AnonHeader(PDU_State.DATA_EXCHANGE, 0, data_or_key=PDU_DataOrKey.DATA, id=self.tuple_ip_id[1]), payload=message)
                pdu_msg.encrypt(self.aes_key) # Message encrypt
                
                conection_table.unverified_put(self.tuple_ip_id, pdu_msg)
                udp_socket.sendto(pdu_msg.get_bytes(), tuple_ip_port)
                

                # Wait for ack process
                begin = unix_time_millis(datetime.datetime.now())
                while True:
                    if conection_table.unverified_empty(self.tuple_ip_id):
                        # If is empty then the packet received ack in the udp read thread
                        break

                    end = unix_time_millis(datetime.datetime.now())
                    if end - begin >= TIMEOUT_MILLIS:
                        begin = unix_time_millis(datetime.datetime.now())
                        udp_socket.sendto(pdu_msg.get_bytes(), tuple_ip_port)
                        
                        
                    

        print("TCP_Read_UDP_Write End")
        #print("conection_table:",conection_table)
        #print("conection_wait:",conection_wait)



class TCP_Receiver(threading.Thread):

    
    def __init__(self,ip_port_peers):
        threading.Thread.__init__(self)
        
        self.TARGET_IP = ip_port_peers[0]
        self.TARGET_PORT = ip_port_peers[1]
        self.overlay_peers = ip_port_peers[2]
        #self.next_id = ip_port_peers[3]
        
        print("Creating thread:",self.overlay_peers)

    def run(self):
        

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind((IP, TCP_PORT))
        s.listen(1)
        print("TCP Server Opened at: {}:{}".format(IP, TCP_PORT))

        while(True):
            conn, tuple_ip_port = s.accept()

            # BEGIN Three way handshake

            # First a node is choosen for tunnel
            node_ip = random.choice(self.overlay_peers)
            print("The choosen one",node_ip,"for id:",Id.next_id)


            # TODO: CHANGE THE THREE WAY HANDSHAKE STRATEGY. UDP SOCKET CAN READ OTHER PACKETS INSTEAD OF SYN,ACK,KEYT))

            hdr_syn = AnonHeader(PDU_State.INIT_CONNECTION,PDU_Flags.SYN,id=Id.next_id)
            pdu_syn = AnonPDU(hdr_syn)
            udp_socket.sendto(pdu_syn.get_bytes(), (node_ip,UDP_PORT))
            print("SYN sent ...")
            
            
            Id.inc()
            tuple_ip_id = (node_ip,hdr_syn.id)
            conection_wait.add(tuple_ip_id, 1, client_soc=conn)