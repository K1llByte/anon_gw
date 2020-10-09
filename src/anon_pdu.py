import rsa
from utils import aes
from utils import checksum, ChecksumNotEqual

class PDU_State:
    INIT_CONNECTION = 1
    DATA_EXCHANGE   = 2
    END_CONNECTION  = 3

    __BIT_SIZE = 2
    @staticmethod
    def validate(state):
        if state > (2**PDU_State.__BIT_SIZE-1) or state <= 0:
            raise ValueError("Invalid state")
        return state

class PDU_Flags:
    SYN = 0b001
    FIN = 0b010
    ACK = 0b100
    
    __BIT_SIZE = 3
    @staticmethod
    def validate(flags):
        if flags >= (2**PDU_Flags.__BIT_SIZE-1) or flags < 0:
            raise ValueError("Invalid flags")
        return flags

class PDU_DataOrKey:
    NOTHING = 0b00 
    P_KEY   = 0b01
    KEY     = 0b10
    DATA    = 0b11

    @staticmethod
    def validate(value):
        if value < 0 or value > 3:
            raise ValueError("Invalid DOK flag")
        return value


def build_anon_header(bytes):
    id = int.from_bytes(bytes[0:4], "big")

    byte = bytes[4]
    state = (byte & 96) >> 5
    flags = (byte & 28) >> 2
    dok = (byte & 3)

    return AnonHeader(state,flags,data_or_key=dok,id=id)

#def prepend_checksum(_bytes):
#    return b"".join([ checksum(_bytes), _bytes ])

# state:       2 bits
# flags:       3 bits
# data_or_key: 2 bit
class AnonHeader:
    #HEADER_BYTE_SIZE = 7

    def __init__(self,state,flags,data_or_key=0b00,id=0):
        
        self.state = PDU_State.validate(state)
        self.flags = PDU_Flags.validate(flags)
        self.data_or_key = PDU_DataOrKey.validate(data_or_key)
        self.id = id

    
    def create_header(self):
        byte = 0b00000000
        byte |= self.state 
        byte <<= 3
        byte |= self.flags
        byte <<= 2
        byte |= self.data_or_key
        
        return b"".join([ self.id.to_bytes(4, byteorder='big'), byte.to_bytes(1, byteorder='big') ])

    #def __str__(self):
    #    return self.create_header()


def build_anon_pdu(message: bytes):
#    cs = checksum(message[2:])
#    if cs != message[:2]:
#        raise ChecksumNotEqual()
    header = build_anon_header(message[:5])
    payload = message[5:]
    return AnonPDU(header,payload)


class AnonPDU:
    def __init__(self, header, payload=None):
        self.header = header
        self.payload = payload

    def get_header(self):
        return self.header

    def get_payload(self):
        return self.payload

    def get_bytes(self):
        if self.payload == None:
            return self.header.create_header()
        else:
            return bytes(b"".join([self.header.create_header(), self.payload]))

    def encrypt(self,key):
        #pass
        
        if self.payload != None and self.payload != b'' and key != None:
            self.payload = aes.encrypt(self.payload,key) 
            print("Len:",len(self.payload))

    def decrypt(self,key):
        #pass
        #print(self.payload)
        #print(key)
        if self.payload != None and self.payload != b'' and key != None:
            print("Len:",len(self.payload))
            self.payload = aes.decrypt(self.payload,key)
        

    def __str__(self):
        return 'Header:\n' +                            \
        str(self.get_header().create_header()) + '\n' + \
        'Payload:\n' +                                  \
        str(self.get_payload()) + ''

# SYN           00010010
# SYN, ACK, KEY 00011011
# ACK, KEY      00011001