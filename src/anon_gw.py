import socket
import _thread as thread
import threading
from shared_data import *
from tcp_receiver import TCP_Receiver, UDP_Receiver



# Thread to always read BUFFER_SIZE bytes from the client and send to the target server 
# until EOF is sended to end the connection
#def client_read_server_write_thread(client_conn,server_conn):
#    while True:
#        buffered_data = client_conn.recv(BUFFER_SIZE)
#        print("received data from client:", buffered_data)
#        if not buffered_data:
#            break
#        server_conn.send(buffered_data)
#        print("sended data to server:", buffered_data)
#
## Thread to always read BUFFER_SIZE bytes from the target server and send to the client 
## until EOF is sended to end the connection
#def server_read_client_write_thread(client_conn,server_conn):
#    while True:
#        buffered_data = server_conn.recv(BUFFER_SIZE)
#        print("received data from server:", buffered_data)
#        if not buffered_data:
#            break
#        client_conn.send(buffered_data)
#        print("sended data to client:", buffered_data)
#
## Server main thread created for each new client
#class ServerThread(threading.Thread):
#    def __init__(self, conn, addr):
#        threading.Thread.__init__(self)
#        self.conn = conn
#        self.addr = addr
#        self.lock = threading.Lock()
#
#    def run(self):
#        self.lock.acquire() #  Remover
#        print('Connection address:', self.addr)
#
#        target_server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        target_server_conn.connect((TARGET_IP, TARGET_PORT))
#
#        #while not end_of_tunnel:
#
#        thread_client_read = threading.Thread(target = client_read_server_write_thread, args = (self.conn,target_server_conn,)).start()
#        thread_server_read = threading.Thread(target = server_read_client_write_thread, args = (self.conn,target_server_conn,)).start()
#        
#        thread_client_read.join()
#        thread_server_read.join()
#
#
#        self.conn.close()
#        target_server_conn.close()
#        self.lock.release() #  Remover
#
#
#def server():
#
#    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#    s.bind((TCP_IP, TCP_PORT))
#    s.listen(1)
#    print("Server Opened at: {}:{}".format(TCP_IP, TCP_PORT))
#
#    while True:
#        conn, addr = s.accept()
#        st = ServerThread(conn, addr)
#        st.start()



# Argument setut



if __name__ == "__main__":
    ip_port_peers = parse_args(sys.argv[1:])
    (target_ip, target_port, overlay_peers) = ip_port_peers

    print("Target {}:{} in peers {}".format(target_ip,target_port,overlay_peers))
    
    #server()
    
    udp_thread = UDP_Receiver((target_ip, target_port, overlay_peers,0))
    tcp_thread = TCP_Receiver((target_ip, target_port, overlay_peers,0))

    udp_thread.start()
    tcp_thread.start()

    udp_thread.join()
    tcp_thread.join()




#import datetime
#import time
#
#epoch = datetime.datetime.utcfromtimestamp(0)
#def unix_time_millis(dt):
#    return (dt - epoch).total_seconds() * 1000.0
#
#TIMEOUT_MILLIS = 1000 # 1 seg de timeout
#
#now = unix_time_millis(datetime.datetime.now())
#
#while True:
#    now2 = unix_time_millis(datetime.datetime.now())
#    if now2 - now >= TIMEOUT_MILLIS:
#        # Send last packet again
#        break
#
#print(now2 - now)



    # example args # target-server 10.3.3.1 port 80 overlay-peers 10.1.1.2 10.4.4.2 10.4.4.3