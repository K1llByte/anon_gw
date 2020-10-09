from queue import Queue

class ConnectionTable:

    def __init__(self,whitelist=None):
        self.connection_table = {} # Map of (ip,port) to public_key and queue


    # Returns True if connection is added
    def add(self,tuple_ip_port,public_key):
        # There is no need for locks because only 1 thread adds (that is the main udp thread creating connections)
        if self.contains(tuple_ip_port):
            return False
        else:
            self.connection_table[tuple_ip_port] = {
                "public_key" : public_key,
                "queue" : Queue(10)
                }
            print("Added to connection table")
            return True


    # Returns True if connection is removed
    def remove(self,tuple_ip_port):
        # There is no need for locks because only 1 thread removes (respective ip_port udp_receiver thread)
        try:
            del self.connection_table[tuple_ip_port]
            print("Removed from connection table")
            return True
        except KeyError:
            return False
        

    # Returns True if contains tuple_ip_port connection
    def contains(self,tuple_ip_port):
        #return tuple_ip_port in self.connection_table
        try:
            self.connection_table[tuple_ip_port]
            return True
        except KeyError:
            return False


    def enqueue(self,tuple_ip_port,pdu):
        self.connection_table[tuple_ip_port]["queue"].put(pdu)     # Thread will block if queue is full

    def dequeue(self,tuple_ip_port):
        return self.connection_table[tuple_ip_port]["queue"].get() # Thread will block if queue is empty

    def get_key(self,tuple_ip_port):
        return self.connection_table[tuple_ip_port]["public_key"]

    
    def __str__(self):
        return str(self.connection_table)