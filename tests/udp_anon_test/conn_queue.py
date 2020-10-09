

class ConnectionWaiting:
    
    def __init__(self,whitelist=None):
        self.wait_conn = {}        # Map of (ip,port) to bool
        self.whitelist = whitelist # List of ip strings

    # Returns True if tuple is added
    def add(self,tuple_ip_port):
        # Alternative checking if whitelist is enabled
        if self.whitelist != None:
            if tuple_ip_port[0] not in self.whitelist:
                return False

        if self.contains(tuple_ip_port):
            return False
        else:
            self.wait_conn[tuple_ip_port] = True
            return True


    # Returns True if tuple is removed
    def remove(self,tuple_ip_port): 
        try:
            del self.wait_conn[tuple_ip_port]
            return True
        except KeyError:
            return False
        

    # Returns True if contains tuple_ip_port
    def contains(self,tuple_ip_port): 
        try:
            self.wait_conn[tuple_ip_port]
            return True
        except KeyError:
            return False