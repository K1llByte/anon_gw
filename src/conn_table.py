from queue import Queue

class ConnectionTable:

    def __init__(self):
        self.connection_table = {} # Map of (ip,port) to key and queue


    # Returns True if connection is added
    def add(self,tuple_ip_id,key):
        # There is no need for locks because only 1 thread adds (that is the main udp thread creating connections)
        if self.contains(tuple_ip_id):
            return False
        else:
            self.connection_table[tuple_ip_id] = {
                "key" : key,
                "queue" : Queue(10),
                "unverified_pdus" : Queue(5),
                "read" : 1,
                "write" : 1
                }
            print("Added to connection table")
            return True


    # Returns True if connection is removed
    def remove(self,tuple_ip_id):
        # There is no need for locks because only 1 thread removes (respective ip_port udp_receiver thread)
        try:
            del self.connection_table[tuple_ip_id]
            print("Removed from connection table")
            return True
        except KeyError:
            return False
        

    # Returns True if contains tuple_ip_id connection
    def contains(self,tuple_ip_id):
        #return tuple_ip_id in self.connection_table
        try:
            self.connection_table[tuple_ip_id]
            return True
        except KeyError:
            return False


    #### PDU Queue related methods ####

    def enqueue(self,tuple_ip_id,pdu):
        self.connection_table[tuple_ip_id]["queue"].put(pdu)     # Thread will block if queue is full

    def dequeue(self,tuple_ip_id):
        return self.connection_table[tuple_ip_id]["queue"].get() # Thread will block if queue is empty

    def get_key(self,tuple_ip_id):
        return self.connection_table[tuple_ip_id]["key"]


    def __close_aux(self, tuple_ip_id, tuple_fields):
        try:
            if self.connection_table[tuple_ip_id][tuple_fields[0]]:
                self.connection_table[tuple_ip_id][tuple_fields[0]] = 0
                return not self.connection_table[tuple_ip_id][tuple_fields[1]]  
            else:
                return -1
        except KeyError:
            return -1

    #### Read/Write channel related methods ####

    # Closes read channel
    # Returns 1 if both read and write are closed 0 otherwise
    # Also returns -1 if tuple_ip_id doesn't exist or read is already closed
    def close_read(self,tuple_ip_id):
        return self.__close_aux(tuple_ip_id,("read","write"))


    # Closes write channel
    # Returns 1 if both write and read are closed 0 otherwise
    # Also returns -1 if tuple_ip_id doesn't exist or write is already closed
    def close_write(self,tuple_ip_id):
        return self.__close_aux(tuple_ip_id,("write","read"))


    def read_write_closed(self, tuple_ip_id):
        try:
            tmp = self.connection_table[tuple_ip_id]
            return tmp["read"] == 0 and tmp["write"] == 0
        except:
            return 1
    
    def read_is_open(self,tuple_ip_id):
        try:
            return self.connection_table[tuple_ip_id]["read"]
        except:
            return 0

    def write_is_open(self,tuple_ip_id):
        try:
            return self.connection_table[tuple_ip_id]["write"]
        except:
            return 0
    

    #### Unverified pdu's related methods ####
    def unverified_empty(self,tuple_ip_id):
        return self.connection_table[tuple_ip_id]["unverified_pdus"].empty()

    def unverified_get(self,tuple_ip_id):
        return self.connection_table[tuple_ip_id]["unverified_pdus"].get()


    def unverified_put(self, tuple_ip_id, pdu):
        return self.connection_table[tuple_ip_id]["unverified_pdus"].put(pdu)



    def __str__(self):
        return "\n" + str(self.connection_table) + "\n"