import feature


class IPv6Address(feature.Feature):
    """
    A feature class representing IPv4 address using CIDR format
    It has two class attributes:
    - _prefix: the IP prefix stored as an integer
    - _prefix_len: the size fo the prefix
    """
        
    @staticmethod
    def IntToDottedIP( intip ):
        """Convert an IP address from an integer to the dotted format"""
        octet = ''
        for exp in [3,2,1,0]:
                octet = octet + str(intip / ( 256 ** exp )) + "."
                intip = intip % ( 256 ** exp )
        return(octet.rstrip('.'))

    @staticmethod
    def DottedIPToInt( dotted_ip ):
        """Convert an IP address from the dotted format to an integer"""
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
                intip = intip + (int(quad) * (256 ** exp))
                exp = exp - 1
        return(intip)
        
    @classmethod
    def create_final_value(className,ip):
        return className(ip)
    
    #A subnet is represented using CIDR notation: a prefix and its length
    def __init__(self,prefix,prefix_len=32,dotted_notation = True):
        """Constructor
            Build an IP address from the prix and the prefix length
            dotted_notation indicates if the prefix is given as an integer or as a dotted format string
        """
        if dotted_notation:
            self._prefix_len = prefix_len
            self._prefix = IPv4Address.DottedIPToInt(prefix)
        else:
            self._prefix_len = prefix_len
            self._prefix = prefix
    
       
    def equivalent(self,f2):
        """Return true if the IP addresses are the same (same subnet)"""
        return self._prefix == f2._prefix and self._prefix_len == f2._prefix_len
        
    def display(self):
        return IPv4Address.IntToDottedIP(self._prefix) + "/"+str(self._prefix_len)

    def final_node(self):
        if self._prefix_len == 32:
            return True
        else:
            return False
        

    def smallest_artificial_prefix(self):
        className = self.__class__.__name__
        
        prefix_len = self._prefix_len - 1
        prefix = self._prefix & ~(2**(32-prefix_len-1))
        return globals()[className](prefix,prefix_len,False)
    
    #~ def smallest_artificial_prefix(self):
        #~ prefix_len = self._prefix_len - 1
        #~ prefix = self._prefix & ~(2**(32-prefix_len-1))
        #~ return IPv4Address(prefix,prefix_len,False)
    
    def direction(self,value,child_directions = []):
        if self._prefix_len == 32:
            return "SAME"
        if self._prefix_len == value._prefix_len:
            return "SAME"
        value = value._prefix
        mask = 2**(32-self._prefix_len-1)
        value = value & mask
        value = value >> (32 - self._prefix_len -1)
        return value
        
        
    def common_prefix(self,value):
        className = self.__class__.__name__
        
        i = 0
        min_len = min(self._prefix_len,value._prefix_len)
        value1 = self._prefix
        value2 = value._prefix
        for i in range(32):
            length_prefix = 32 - i
            if value1 == value2 and (length_prefix<=(min_len)):
                common_prefix = value1 * 2**i
                return globals()[className](common_prefix,length_prefix,False)
            value1 = value1 >> 1
            value2 = value2 >> 1
        return globals()[className](0,0,False)
        
    def distance(self,element):
        if element is not None:
            res = 1- (2**(self.common_prefix(element)._prefix_len) / float(2** 32))
            assert res <= 1.0
            #print "%s/%s"%(self.IntToDottedIP(self._prefix),self._prefix_len), "%s/%s"%(self.IntToDottedIP(element._prefix),element._prefix_len),res,self.common_prefix(element)
            return res
        else:
            return 1.0
        '''
        if element is None:
            res = editdist.distance(bin(self._prefix),'') / float(len(bin(self._prefix)))
            assert res <= 1.0 
            return res
        else:
            res = editdist.distance(bin(self._prefix),bin(element._prefix)) / float(max(len(bin(self._prefix)),len(bin(element._prefix))))
            if bin(element._prefix) == bin(self._prefix): 
                assert res == 0
            assert res <= 1.0 
            return res
        '''                         
    def similarity(self,element):
        return self.distance(element)
    #~ def common_prefix(self,value):
        #~ i = 0
        #~ min_len = min(self._prefix_len,value._prefix_len)
        #~ value1 = self._prefix
        #~ value2 = value._prefix
        #~ for i in range(32):
            #~ length_prefix = 32 - i
            #~ if value1 == value2 and (length_prefix<=(min_len)):
                #~ common_prefix = value1 * 2**i
                #~ return IPv4Address(common_prefix,length_prefix,False)
            #~ value1 = value1 >> 1
            #~ value2 = value2 >> 1
        #~ return IPv4Address(0,0,False)
        #~ 
    def _maxval(self):
		return None
		
    def _minval(self):
		return None
		
    def subprefix(self,sub):
        return self.common_prefix(sub)._prefix_len >= self._prefix_len

    def get_prefix(self):
        return self._prefix
        
    def get_prefix_len(self):
        return self._prefix_len
