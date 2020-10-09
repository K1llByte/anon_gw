#from exception import ValueError

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
    KEY = 0b1
    DATA = 0b0

    @staticmethod
    def validate(bit):
        if bit != 0 and bit != 1:
            raise ValueError("Invalid DOK flag")
        return bit


def build_anon_header(byte):
    state = (byte & 48) >> 4
    flags = (byte & 14) >> 1
    dok = (byte & 1)
    return AnonHeader(state,flags,dok)


# state:       2 bits
# flags:       3 bits
# data_or_key: 1 bit
class AnonHeader:
    #state = None
    #flags = None
    #data_or_key = None
    HEADER_BYTE_SIZE = 1

    def __init__(self,state,flags,data_or_key=0b0):
        self.state = PDU_State.validate(state)
        self.flags = PDU_Flags.validate(flags)
        self.data_or_key = PDU_DataOrKey.validate(data_or_key)

    def create_header(self):
        byte = 0b00000000
        byte |= self.state 
        byte <<= 3
        byte |= self.flags
        byte <<= 1
        byte |= self.data_or_key
        
        return byte

    #def __str__(self):
    #    return self.create_header()


def build_anon_pdu(message: bytes):
    header = build_anon_header(message[0])
    payload = message[1:]    
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
        #tmp = bytearray()
        #tmp.append(self.header.create_header())
        #tmp.append(self.payload)
        if self.payload == None:
            return bytes(self.header.create_header().to_bytes(1, byteorder='big'))
        else:
            return bytes(b"".join([self.header.create_header().to_bytes(1, byteorder='big'), self.payload]))

    def __str__(self):
        return 'Header:\n' +                                 \
        str(bin(self.get_header().create_header())) + '\n' + \
        'Payload:\n"' +                                      \
        str(self.get_payload()) + '"'

# SYN           00010010
# SYN, ACK, KEY 00011011
# ACK, KEY      00011001


if __name__ == "__main__":
    hdr_syn = AnonHeader(PDU_State.INIT_CONNECTION,PDU_Flags.SYN)
    hdr_syn_ack_key = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.SYN | PDU_Flags.ACK,  PDU_DataOrKey.KEY)
    hdr_ack_key = AnonHeader(PDU_State.INIT_CONNECTION, PDU_Flags.ACK,  PDU_DataOrKey.KEY)
    
    pdu_syn = AnonPDU(hdr_syn)
    pdu_syn_ack_key = AnonPDU(hdr_syn_ack_key,b'server public_key')
    pdu_ack_key = AnonPDU(hdr_ack_key,b'client public_key')

    print(pdu_syn)
    print()
    print(pdu_syn_ack_key)
    print()
    print(pdu_ack_key)
    #b = b'!olamundo'
    #pdu = AnonPDU(b)
    #print(bin(pdu.get_header().create_header()))
    #print(pdu.get_payload())