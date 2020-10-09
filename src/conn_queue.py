

class ConnectionWaiting:
    
    def __init__(self,whitelist=None):
        self.wait_conn = {}        # Map of (ip,port) to bool
        self.whitelist = whitelist # List of ip strings

    # Returns True if tuple is added
    def add(self, tuple_ip_id, value=2, client_soc=None):
        
        # Alternative checking if whitelist is enabled
        if self.whitelist != None:
            if tuple_ip_id[0] not in self.whitelist:
                return False

        if tuple_ip_id in self.wait_conn:
            return False
        else:
            self.wait_conn[tuple_ip_id] = {
                "value" : value ,
                "client_soc" : client_soc
            }
            print("Added to Waiting connection table")
            print(self)
            return True


    # Returns True if tuple is removed
    def remove(self,tuple_ip_id):
        try:
            del self.wait_conn[tuple_ip_id]
            print("Removed from Waiting connection table")
            print(self)
            return True
        except KeyError:
            print(" DIDNT REMOVE FROM WAITING !!!")
            return False
        

    # Returns state if contains tuple_ip_id
    def get(self,tuple_ip_id): 
        try:
            return self.wait_conn[tuple_ip_id]["value"]
        except KeyError:
            return False

    def get_client_soc(self,tuple_ip_id):
        try:
            return self.wait_conn[tuple_ip_id]["client_soc"]
        except KeyError:
            return False

    def __str__(self):
        return "\n Conection Wait: " + str(self.wait_conn) + "\n"