#Author : Jerome Francois, Lautaro Dolberg (first.second@uni.lu)
#Date : 16/05/2012
#All rights reserved
#GPL version 2.0 to be found at: http://www.gnu.org/licenses/gpl-2.0.txt
#2012 University of Luxembourg - Interdisciplinary Centre for Security Reliability and Trust (SnT)
import re
import levenshtein
import editdist

class Feature:
    """
    Class representing a feature o use as a dimension of the nD trees
    """
    
    def equivalent(f2):
        """Return true if the feature is equivalent (equals) to f2"""
        raise NotImplementedError
        
    def display():
        """Display the feature
        Two different values have to output differently if DOT output is asked
        since it is used in node identifier"""
        raise NotImplementedError

    def final_node():
        """Is the object a final node, i.e. it cannot have any children"""
        raise NotImplementedError
        
    def smallest_artificial_prefix():
        """Create the smallest feature enclosing the current one"""
        raise NotImplementedError
    
    def direction(value, child_directions = []):
        """Get the direction from the current node regarding a value
        child_directions is the list of already used directions if needed
        """
        
        raise NotImplementedError
        
    def common_prefix(self,value):
        """Get the common prefix (smallest ennglobing class) of the current object and a value"""
        raise NotImplementedError
        
    def subprefix(self,sub):
        """Test if sub is enclosed within the current feature"""
        raise NotImplementedError
        
    def __str__(self):
        return self.display()
    
    def __repr__(self):
        return self.__str__()
        
    @staticmethod
    def create_final_value(arg):
        """Method called by the program to create leaf nodes"""
        raise NotImplementedError
                       
class IPv4Address(Feature):
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
        

class Domain(Feature):
    """
    A feature class representing DNS domain
    There is one attribute: the domain
    """  
    
    @staticmethod
    def create_final_value(domain):
        """We use .ROOT as the generic root for domain trees"""
        return Domain("$."+domain+".ROOT")
    
    
    def __init__(self,domain):
        self._domain = domain
       
    def equivalent(self,f2):
        """Return true if domain are exactly the same"""
        return self._domain == f2._domain
        
    def display(self):
        return str(self._domain)
        

    def final_node(self):
        """Return always false because there is no limitation to split a domain (unlike IP /32 subnets)"""
        #Correction
        if self._domain[0] == "$":
            return  True
        return False
        
    def smallest_artificial_prefix(self):
        split = self._domain.split(".",1)
        if len(split)>1:
            return Domain(split[1])
        else:
            return Domain("ROOT")

    def similarity(self,element):
        return self.distance(element)
    
    def distance(self,element):
        if element is None:
            return 1.0
        d1 = self._domain.split(".")
        d2 = element._domain.split(".")
        
        d1 = levenshtein.safe_remove("$", d1)
        d1 = levenshtein.safe_remove("ROOT", d1)
        
        d2 = levenshtein.safe_remove("$", d2)
        d2 = levenshtein.safe_remove("ROOT", d2)
        
        total = float(max(len(d1),len(d2)))
        edist = levenshtein.levenshtein_domain(self._domain,element._domain) 
        res = edist / total if total > 0.0 else 0.0 
        if d1 == d2: assert res == 0
        #print self._domain,element._domain,d1,d2,edist,res
        try:
            assert res <= 1.0
        except:
            print d1,d2,edist,total
        return res 
    
    def direction(self,value,child_directions = []):
        if self.equivalent(value):
            return "SAME"
        find = re.search("(.*)\."+str(self._domain).replace(".","\."),value._domain)
        split = find.group(1).split(".")
        return split[len(split)-1]
        
    
    def common_prefix(self,value):
        
        
        split1 = self._domain.split(".")
        split2 = value._domain.split(".")
                
        prefix = ""
        while len(split1)> 0 and len(split2) > 0:
            v1 = split1.pop()
            v2 = split2.pop()
            
            if v1 == v2:
                prefix = v1 + "." + prefix
            else:
                break
            
        return Domain(prefix[:len(prefix)-1])
        
        
    def subprefix(self,sub):
    
        if self.equivalent(sub):
            return True
        a ="(.*)\."+str(self._domain).replace(".","\.")
        find = re.search(a,sub._domain)
        
        if find:
            return True
        else:
            return False
        
class SIP(Domain):
    def __str__(self):
        return self._domain
    def _maxval(self):
        return None
        
    def _minval(self):
        return None  
    dictApplis = {
        "REQUEST": ["INVITE",
                    "ACK",
                    "BYE",
                    "CANCEL",
                    "OPTIONS",
                    "REGISTER",
                    "PRACK",
                    "SUBSCRIBE",
                    "NOTIFY",
                    "PUBLISH",
                    "INFO",
                    "REFER",
                    "MESSAGE",
                    "UPDATE"],


        "STATUS": {
                100: "Provisional.Trying",
                180: "Provisional.Ringing",
                181: "Provisional.CallIsBeingForwarded",
                182: "Provisional.Queued",
                183: "Provisional.SessionProgress",
                200: "Success.OK",
                202: "Success.Accepted",
                300: "Redirect.MultipleChoices",
                301: "Redirect.MovedPermanently",
                302: "Redirect.MovedTemporarily",
                305: "Redirect.UseProxy",
                380: "Redirect.AlternativeService",
                400: "ClientError.BadRequest",
                401: "ClientError.Unauthorized",
                402: "ClientError.PaymentRequired",
                403: "ClientError.Forbidden",
                404: "ClientError.NotFound",
                405: "ClientError.MethodNotAllowed",
                406: "ClientError.NotAcceptable",
                407: "ClientError.ProxyAuthenticationRequired",
                408: "ClientError.RequestTimeout",
                409: "ClientError.Conflict",
                410: "ClientError.Gone",
                413: "ClientError.RequestEntityTooLarge",
                414: "ClientError.RequestURITooLong",
                415: "ClientError.UnsupportedMediaType",
                416: "ClientError.UnsupportedURIScheme",
                420: "ClientError.BadExtension",
                421: "ClientError.ExtensionRequired",
                422: "ClientError.SessionIntervalTooSmall",
                423: "ClientError.IntervalTooBrief",
                480: "ClientError.TemporarilyUnavailable",
                481: "ClientError.DoesNotExist",
                482: "ClientError.LoopDetected",
                483: "ClientError.TooManyHops",
                484: "ClientError.AddressIncomplete",
                485: "ClientError.Ambiguous",
                486: "ClientError.BusyHere",
                487: "ClientError.RequestTerminated",
                488: "ClientError.NotAcceptableHere",
                491: "ClientError.RequestPending",
                493: "ClientError.Undecipherable",
                500: "ServerError.ServerInternalError",
                501: "ServerError.NotImplemented",
                502: "ServerError.BadGateway",
                503: "ServerError.ServiceUnavailable",
                504: "ServerError.ServerTime-out",
                505: "ServerError.VersionNotSupported",
                513: "ServerError.MessageTooLarge",
                580: "ServerError.PreconditionFailure",
                600: "GlobalError.BusyEverywhere",
                603: "GlobalError.Decline",
                604: "GlobalError.DoesNotExistAnywhere",
                606: "GlobalError.NotAcceptable"
                   
        }
        
    }
    @staticmethod
    def create_final_value(app):
        """An application is represented by a protocol and a port number"""
        (mtype,code) = app.strip().split(",")
        if mtype == 'STATUS': 
            code = int(code)
        newApp = mtype
        if mtype == "REQUEST":
            newApp= "%s.REQUEST"%code
        else:
            if code in SIP.dictApplis['STATUS'].keys():
                apps = SIP.dictApplis['STATUS'][code].split(".")
                for e in apps:
                    newApp = e + "."+ newApp
        return SIP("$."+newApp+".ROOT")
        
                
class Application(Domain):
    """
    A class representing application regarding the protocol they use
    """
    
    def __str__(self):
        return self._domain
    
    dictApplis = {
        "TCP" : {
            143 : "Mail.Get.IMAP.v2",
            220 : "Mail.Get.IMAP.v3.TCP",
            993 : "Mail.Get.IMAP.SSL",
            109 : "Mail.Get.Pop.v2",
            110 : "Mail.Get.Pop.v3",
            995 : "Mail.Get.Pop.v3.Secure",
            25 : "Mail.Send.SMTP",
            465 : "Mail.Send.SMTP.Secure",
            587 : "Mail.Send.SMTP.MessageSubmission",
            2525 : "Mail.Send.SMTP.alternative.1",
            3535 : "Mail.Send.SMTP.alternative.2",
            80 : "Web.HTTP",
            443 : "Web.HTTP.Secure",
            3306 : "DB.MySQL.TCP",
            5432 : "DB.PostgreSQL.UDP",
            53 : "Name.DNS.TCP",
            43 : "Name.Whois",
            445 : "FileSharing.SMB",
            20 : "FileSharing.FTP.Data",
            21 : "FileSharing.FTP.Command",
            989 : "FileSharing.FTP.Data.Secure",
            990 : "FileSharing.FTP.Command.Secure",
            115 : "FileSharing.SFTP",
            1194 : "RemoteAccess.VPN.OpenVPN",
            5000 : "RemoteAccess.VPN.VTune",
            22 : "RemoteAccess.SSH",
            3389: "RemoteAccess.Microsoft.TerminalServices",
            
            
        },
        "UDP" : {
            220 : "Mail.Get.IMAP.v3.UDP",
            80 : "Web.HTTP",
            3306 : "DB.MySQL.UDP",
            5432 : "DB.PostgreSQL.UDP",
            53 : "Name.DNS.UDP",
            69 : "FileSharing.TFTP",
            989 : "FileSharing.FTP.Data.Secure",
            990 : "FileSharing.FTP.Command.Secure",
            1194 : "RemoteAccess.VPN.OpenVPN",
            5000 : "RemoteAccess.VPN.VTune",
            }
        }

    def equivalent(self,f2):
		if self.final_node() and f2.final_node():
				return "SAME"
		else:
				return self._domain == f2._domain
    '''				
    def distance(self,element):
        
        d1 = self._domain.split(".")
        if element is None:
            return 1.0
        d2 = element._domain.split(".")
        if d1 == d2: assert (len(d1) - len([d for d in d1 if d in d2])) / float(len(d1)) == 0
        return (len(d1) - len([d for d in d1 if d in d2]) )/ float(len(d1))
    '''    
    @staticmethod
    def create_final_value(app):
        """An application is represented by a protocol and a port number"""
        (port,proto) = app.strip().split(",")
        port = int(port)
        
        if proto in Application.dictApplis.keys():
            if port in Application.dictApplis[proto].keys():
                apps = Application.dictApplis[proto][port].split(".")
                newApp = ""
                for e in apps:
                    newApp = e + "."+ newApp
                return Application("$."+newApp+"ROOT")
        #if port < 2048:
        #    print proto,port
        return Application("$."+"Others"+".ROOT")
        
    def _maxval(self):
		return None
		
    def _minval(self):
		return None    
        
class Taxonomy(Feature):
    """
    A generic class for representing a taxonomy
    """
    
    dict = {}
    
    @staticmethod
    def read_file(filename):
        
        levels = {}
        in_file = open(filename)
        
        for line in in_file:
            line = line.strip()
            
            find = re.search("(\.*)(.*)",line)
            if find:
                print find.group(1)
                print find.group(2)
            
        
        
    
    
class Location(Feature):
    
    def __init__(self,x,y):
        self.x = Range.create_final_value(x)
        self.y = Range.create_final_value(y)
        
    @staticmethod
    def create_final_value(val_dim):
        """A final value is a single point, min and max are the same"""
        x,y = val_dim.split()[0],val_dim.split()[1]
        return Location(x,y)
    
    def equivalent(self,f2):
        return self.x.equivalent(f2.x) and self.y.equivalent(f2.y) 
    
    def display(self):
        return "X: "+ self.x.display() +" Y:"+ self.y.display()
    
    def final_node(self):
        return self.x.final_node() and self.y.final_node()
    
    def direction(self,value, child_directions=[]):
        dx = self.x.direction(value.x, child_directions)
        dy = self.y.direction(value.y, child_directions)
        if dx == 1 and dy == 1:
            return 2
        if dx == -1 and dy == -1:
            return -1
        if dx == 1 and dy == -1:
            return 1
        if dx == -1 and dy == 1:
            return 0
        
    def common_prefix(self, value):
        l = Location(0,0)
        l.x = self.x.common_prefix(value.x)
        l.y = self.y.common_prefix(value.y)
        return l
    
    def subprefix(self, sub):
        return self.x.subprefix(sub.x) and self.y.subprefix(sub.y)
        
class Range(Feature):
    """
    A feature class representing a range on a float dimension (may be used for GPS coordinate)
    """  
    
    precision = 0.000001
    
    @staticmethod
    def setPrecision(precision):
        Range.precision = precision
        
    
    @staticmethod
    def create_final_value(val_dim):
        """A final value is a single point, min and max are the same"""
        return Range(val_dim,val_dim,val_dim)
    
    
    def __init__(self,minval,maxval,middle):
        self._minval = float(minval)
        self._maxval = float(maxval)
        self._middle = float(middle)
        
       
    def equivalent(self,f2):
        """Return true if the difference is below the precision"""
        if abs(self._minval - f2._minval) < Range.precision and abs(self._maxval - f2._maxval) < Range.precision:# and abs(self._middle - f2._middle) < Range.precision:
            return True
            
        return False
        
    def display(self):
        #return str(self._minval)+"/"+str(self._maxval)+"/"+str(self._middle)
        return "%.2f/%.2f/%.2f" % (self._minval,self._maxval,self._middle)
        
        

    def final_node(self):
        """Final node if the range is below the precision"""
        if abs(self._minval - self._maxval) < Range.precision:
            return True
        return False
        
    
    
    
    def direction(self,value,child_directions):
        #~ if self.equivalent(value):
            #~ print self,value
            #~ return "SAME"
        #print "*",value._minval, value._maxval, self._middle
        
        if  value._minval < self._middle: 
            if value._maxval <= self._middle:
                return -1
        elif value._minval >= self._middle: 
            if value._maxval >= self._middle:
                return 1
        
        else:
            #~ print self
            #~ print value
            #~ 
            #~ print child_directions
            raise NameError('Unable to find a direction')
    #~ 
    

    def common_prefix(self,value):
        
        
        
        if self._minval < value._minval:
            middle = 0.5*(self._maxval + value._minval)
        else:
            middle = 0.5*(self._minval + value._maxval)
            
        
        if self._maxval <= value._minval:
            middle = 0.5*(self._maxval + value._minval)
        elif self._minval >= value._maxval:
            middle = 0.5*(self._minval + value._maxval)
        elif self._minval <= value._minval and self._maxval >= value._maxval:
            middle = self._maxval
        elif self._minval >= value._minval and self._maxval <= value._maxval:
            middle = value._maxval
        else:
            raise NameError('Intersection of ranges is not possible')
            
        
        return Range(min(self._minval,value._minval),max(self._maxval,value._maxval),middle)
        
    def subprefix(self,sub):
    

        if self.equivalent(sub):
            return True
        
        
        if sub._minval <= self._maxval and sub._minval >=self._minval and  sub._maxval <= self._maxval and sub._maxval >=self._minval:
            return True
        else:
            return False
        
        
class Range2(IPv4Address):
    """
    A feature class representing a range on a float dimension (may be used for GPS coordinate)
    """  
    
   
    def __init__(self,prefix,prefix_len=32,dotted_notation = True):
        scaleup = 100000
        decalage = 180
        """Constructor
            Build an IP address from the prefix and the prefix length
            dotted_notation indicates if the prefix is given as an integer or as a dotted format string
        """
        if dotted_notation:
            if prefix_len != 32:
                raise NameError("Input value should be final one")
            self._prefix_len = prefix_len
            self._prefix = int((float(prefix) + decalage) * scaleup)
            self._minval = prefix
            self._maxval = prefix
        else:
            self._prefix_len = prefix_len
            self._prefix = prefix
            
            self._minval = (1.0*prefix / scaleup) - decalage
            if prefix_len < 32:
                self._maxval = (1.0*(prefix+2**(32-prefix_len)) / scaleup) - decalage
            else:
                self._maxval = self._minval
            
