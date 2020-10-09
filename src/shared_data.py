from conn_queue import ConnectionWaiting
from conn_table import ConnectionTable
import rsa
import sys
import socket
import threading

#from shared_data import BUFFER_SIZE, TCP_PORT, UDP_PORT, IP, public_key, private_key, udp_socket, next_id, conection_wait, conection_table

BUFFER_SIZE  = 1024
UDP_BUFFER_SIZE  = 2048
HEADER_SIZE = 5

TCP_PORT = 80
UDP_PORT = 6666

TIMEOUT_MILLIS = 1000

IP = '0.0.0.0'

(public_key, private_key) = rsa.newkeys(1024,poolsize=4)

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind((IP, UDP_PORT))

TARGET_IP = ''
TARGET_PORT = 80
overlay_peers = []



#next_id = 0


class Id:
    next_id = 0
    lock = threading.Lock()

    @staticmethod
    def inc():
        Id.lock.acquire()
        Id.next_id += 1
        Id.lock.release()

def parse_args(argv):
    #global overlay_peers
    #global TARGET_PORT
    #global TARGET_IP

    # Just a temporary 'macro' for printing errors
    perror = lambda txt : print("error:",txt,file=sys.stderr)

    i = 0
    while i < len(argv):
        # Target argument
        if argv[i] in ("-target-server","target-server"):
            try:
                target_ip = argv[i+1]
                i += 1
            except IndexError:
                perror("'target-server' argument not provided")
                exit(2)
        # Port argument
        elif argv[i] in ("-port","port","-p"):
            try:
                target_port = int(argv[i+1])
                if target_port < 0 or target_port > 65535:
                    perror("invalid 'port' value")
                    exit(2)
                i += 1
            except IndexError:
                perror("'port' argument not provided")
                exit(2)
            except ValueError:
                perror("'port' is an invalid integer")
                exit(2)
        
        elif argv[i] in ("-overlay-peers","overlay-peers"):
            overlay_peers = argv[i+1:].copy()
            break

        else:
            perror("unknown argument '{}'".format(argv[i]))
            #print("error: invalid option -- '{}'".format(argv[i]))
            #print("Try '--help' for more information")
        
        i += 1
    
    return (target_ip, target_port, overlay_peers)

(TARGET_IP, TARGET_PORT, overlay_peers) = parse_args(sys.argv[1:])

conection_wait = ConnectionWaiting(whitelist=overlay_peers)
conection_table = ConnectionTable()



#class Data:
#    def __init__(self):
#        self.TARGET_IP = ''
#        self.TARGET_PORT = 80
#        self.overlay_peers = []
#
#        self.next_id = 0

#data = Data()


