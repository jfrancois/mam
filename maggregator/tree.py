import re
        
class Tree:
    """
    A class representing a tree, this is a wrapper for a node which is also a tree
    It contains a specific node, the root
    """
    
    def __init__(self,dim=None):
        """Constructor from a list of dimension"""
        self._root = None
        self._dim = dim
        self._list_nodes = []
        
    def increase_age_tree(self):
        for n in self._list_nodes:
            n.increase_age()
        
    def is_empty(self):
        """Test if the tree is empty"""
        if self._root == None:
            return True
        else:
            return False
        
    def preorder(self):
        if self.is_empty():
            return []
        return self.get_root().preorder()
    
    def set_root(self,node):
        """Set a node as the root"""
        self._root = node
       
    def get_root(self):
        """Get the root"""
        return self._root   
        
    def get_dim(self):
        """Get the list of dimensions used in the tree"""
        return self._dim
        
        
    def display(self):
        """Display the tree by displaying from the root"""
        return self._root.display(0)
        
    def display_aggregate(self,threshold,total):
        """Display the tree as aggregated by displaying from the root"""
        return self._root.display_aggregate(threshold,total,0)[0]
    
    def aggregate(self,threshold,total):
        """Aggregate the tree from the root"""
        return self._root.aggregate(threshold,total,0)
    
    def display_preaggregate(self,total):
        """Display the tree after having been aggregated"""
        return self._root.display_preaggregate(total,0)[0]

    def dot_preaggregate(self,total):
        """Display the tree after having been aggregated"""
        res = "digraph G {\n node [shape=record];"
        res += self._root.dot_preaggregate(total,0,1)[0]
        res += "}"
        return res
        
    def gmap_preaggregate(self,total):
        """Display the tree after having been aggregated"""
        
        res = self._root.gmap_preaggregate(total,0,1)[0]
        return res



class Node:
    """Superclass of Node, a node is a tree"""
        
                
    #key is a dictionnary with
    #key = name of the feature
    #value = value of the feature
    def __init__(self,key,init_value,children,tree=Tree(),parent=None):
       
        self._key = key
        self._value = init_value
        self._children = children
        self._parent = parent
        
        self._tree = tree
        self._aggrValue = self.getDefaultAggr()
        self._age = 0
        self._uses = 0
        
        
        
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "- NODE: %s %s %s %s -" % (self._value,self._key,self._age,self._uses)

    #Default (initial) agrgegated value has to be defined 
    def getDefaultAggr(self):
        raise NotImplementedError
       
    #Aggregation has to be defined
    def add_aggr_value(self,add):
        raise NotImplementedError
        
    def get_aggr_value(self):
        return self._aggrValue
        
    def set_aggr_value(self,val):
        self._aggrValue = val
        
    def get_tree(self):
        return self._tree
    
    def integrate_node(self):    
        if self.get_tree().is_empty():
            self.get_tree().set_root(self)
        else:
            self.get_tree().get_root().insert_node(self,self.get_tree().get_dim())
        #self.get_tree().increase_age_tree()
        
    #update the value with a new one, has to be implemented
    def update_value(self,value_to_add):
        raise NotImplementedError
    
    def get_age(self):
        return self._age
    
    def get_uses(self):
        return self._uses
    
    def get_tree(self):
        return self._tree    
    
    def get_key(self):
        return self._key
        
    def get_value(self):
        return self._value
        
    def get_children(self):
        return self._children
        
    def get_parent(self):
        return self._parent
    
    def set_children(self,children):
        self._children = children
        
    def set_parent(self,parent):
        self._parent = parent
        
    def set_tree(self,tree):
        self._tree = tree
        
    def equivalent(self,other,dim):
        for k in dim:
            return self.get_key()[k].equivalent(other.get_key()[k])
            
    def increase_age(self):
        self._age +=1
    def increment_uses(self):
        self._uses +=1
            
  
    def display_intern(self,children,dim,level):
        """Display the children of a node, i.e. the nodes accessed through of the different dimensions"""
        if not (children == None or children == {}):
            if len(dim) == 0:
                return children.display(level)
            else:
                d = dim[0]
                res = ""
                
                for direction in children[d]:
                    res = res + self.display_intern(children[d][direction],dim[1:],level) 
                return res
        else:
            return ""
            
    
    def display(self,level=0):
        """Display a node: its key and the children"""
        
        indent = "   "*level
        
        toDisplay = "["
        for k in self.get_tree().get_dim():
            toDisplay = toDisplay + str(k) +"-->"+self.get_key()[k].display()+" "
        toDisplay = toDisplay + str(self._value)+ " age: %s uses: %s]" % (self._age,self._uses)
        res = indent+toDisplay+"\n"
        res = res + self.display_intern(self.get_children(),self.get_tree().get_dim(),level+1)
        
        return res    
        
    def display_key(self):
        """debugging method to display the key of a node"""
        toDisplay = "["
        for k in self.get_tree().get_dim():
            toDisplay = toDisplay + str(k) +"-->"+self.get_key()[k].display()+" "
        toDisplay = toDisplay + "]"
        res = toDisplay+"\n"
        return res  
    
            
    def display_preaggregate(self,total,level):
        """
        Display a node which was previously aggregated
        total is the total value in the tree (for %)
        level is the indentation level
        """
        
        aggr_all = 0.0
        intern_str = ""
        
        #Dsiplay the children and get the aggregated values which are summed up
        for c in self.get_children():
            res,aggr = c.display_preaggregate(total,level+1)
            aggr_all += aggr
            intern_str += res
        
        percent = self.get_value()
        percent2 = aggr_all + self.get_value()
        toDisplay = ""
        
        
        #Display the current node
        
        #toDisplay = "["
        for k in self.get_tree().get_dim():
            #toDisplay = toDisplay + str(k) +"-->"+Types.display(self.get_key()[k],v)+" "
            toDisplay = toDisplay + self.get_key()[k].display()+" "
        #toDisplay = toDisplay + "]"
        toDisplay += " "+str(int(percent))+" ("+"%.2f" % (100.0*percent/total)+"% / "+"%.2f" % (100.0*percent2/total)+"%)  "#+ "%.2f" % (100.0*self.get_aggr_value()/total)+"%"
        
        indent = "   "*level
        current_str = indent+toDisplay+" \n "+intern_str
            
        return current_str,aggr_all+self.get_value()
        
        
    def dot_preaggregate(self,total,level,ind):
        """
        Display a node which was previously aggregated
        total is the total value in the tree (for %)
        level is the indentation level
        """
        
        aggr_all = 0.0
        intern_str = ""
        
        dot = ""
        indChild = ind +1
        #Dsiplay the children and get the aggregated values which are summed up
        for c in self.get_children():
            dot += str(ind) +" -> "+str(indChild)+";\n"
            res,aggr,indNew = c.dot_preaggregate(total,level+1,indChild)
            indChild = indNew +1
            aggr_all += aggr
            intern_str += res
        
        percent = self.get_value()
        percent2 = aggr_all + self.get_value()
        toDisplay = ""
        
        
        #Display the current node
        #B [label="{{B|2}|001010}"];
        dot +=str(ind)+" [label=\"{"
        
        for k in self.get_tree().get_dim():
            #toDisplay = toDisplay + str(k) +"-->"+Types.display(self.get_key()[k],v)+" "
            dot+= str(k) +": "+self.get_key()[k].display()+"|"
        
        #dot+= "{"+"age: %s|uses: %s}|" % (self._age,self._uses)   
        #toDisplay = toDisplay + "]"
        dot+="{"+"%.2f" % (100.0*percent/total)+"%|"+"%.2f" % (100.0*percent2/total)+"%}}\"]\n"
       
        
       
        current_str = dot+" \n "+intern_str
            
            
        return current_str,aggr_all+self.get_value(),indChild
        
        
    #FOR TESTS ONLY
    def gmap_preaggregate(self,total,level,ind):
        
        
        aggr_all = 0.0
        intern_str = ""
        
        dot = "var rect = [\n"
        

        indChild = ind +1
        #Dsiplay the children and get the aggregated values which are summed up
        for c in self.get_children():
            
            res,aggr,indNew = c.gmap_preaggregate(total,level+1,indChild)
            indChild = indNew +1
            aggr_all += aggr
            intern_str += res
        
        percent = self.get_value()
        percent2 = aggr_all + self.get_value()
        toDisplay = ""
        
       
        
        dim_values = []
        for k in self.get_tree().get_dim():
            #toDisplay = toDisplay + str(k) +"-->"+Types.display(self.get_key()[k],v)+" "
            dim_values.append((self.get_key()[k]._minval,self.get_key()[k]._maxval))

        dot += "new google.maps.LatLng(%s, %s),\n" % (dim_values[0][0],dim_values[1][0])
        dot += "new google.maps.LatLng(%s, %s),\n" % (dim_values[0][0],dim_values[1][1])
        dot += "new google.maps.LatLng(%s, %s),\n" % (dim_values[0][1],dim_values[1][1])
        dot += "new google.maps.LatLng(%s, %s),\n" % (dim_values[0][1],dim_values[1][0])
        dot += "new google.maps.LatLng(%s, %s)\n" % (dim_values[0][0],dim_values[1][0])
        dot += "];\n"
        
        dot+= "shape = new google.maps.Polygon({\n"
        dot+= " paths: rect,"
        dot+= "strokeColor: get_random_color(),"
        dot+= "strokeOpacity: 0.8,"
        dot+= "strokeWeight: 4,"
        dot+= "fillColor: \"#FF0000\","
        dot+= "fillOpacity: 0.05});"

        dot+= "shape.setMap(map);"
       
        #~ dot += "var infowindow = new google.maps.InfoWindow({\n"
        #~ dot += "content: \"%s\"    });\n" % (self)

       #~ 
        #~ dot+= "google.maps.event.addListener(shape, 'click', function() {\n"
        #~ dot+= "infowindow.open(map,new google.maps.LatLng(%s, %s));\n" % (dim_values[0][0],dim_values[1][0])
        #~ dot+= "});\n"
       
        dot += "google.maps.event.addListener(shape, 'click', showArrays);\n"
        current_str = dot+" \n "+intern_str
            
        return current_str,aggr_all+self.get_value(),indChild
    
    def intern_preorder(self,children,dim):
        if len(dim) == 0:
            return children.preorder()
        else:
            d = dim[0]
            res = []
            if d in children.keys():
                    for direction in children[d].keys():
                        if children[d][direction] != None or children[d][direction] != {}:
                            res += self.intern_preorder(children[d][direction],dim[1:]) 
            return res
        
    def preorder(self):
        res = [self]
        #After Aggregation
        if type(self.get_children()) == list:
            for x in self.get_children():
                res += x.preorder()
        #Before Aggregation      
        elif not (self.get_children() == None or self.get_children() == {}):
            res+=self.intern_preorder(self.get_children(), self.get_tree().get_dim())
         
        return res
            
    def intern_aggregate(self,children,dim,level,threshold,total,keep_root=False):
        #print "ia"    
        if not children == None or children == {}:
        
            if len(dim) == 0:
                #Final node of internal tree = node
                #This node is displayed
                return children.aggregate(threshold,total,level,keep_root)
            else:
                d = dim[0]
                aggr_comb = 0.0
                new_child =[]
                new_nodes = []
                tot_aggr = 0.0
                try:
                    #We explore the current dimension by extracting the different value for each direction
                    if d in children.keys():
                        for direction in children[d].keys():
                            if children[d][direction] != None or children[d][direction] != {}:
                                
                                #schildren = sorted(children[d][direction],key=lambda x: x._uses/x._age)
                                
                                aggr1, new_child1, new_nodes1, tot_aggr1 = self.intern_aggregate(children[d][direction],dim[1:],level,threshold,total) 
                                aggr_comb += aggr1
                                tot_aggr += tot_aggr1
                                new_child.extend(new_child1)
                                new_nodes.extend(new_nodes1)
                            
                    return aggr_comb,new_child,new_nodes, tot_aggr
                except:
                    raise
                
        else:
            return 0.0, [], [],0.0
            
    def aggregate(self,threshold,total,level=0,keep_root=False):
        #print "a"
        if total == 0:
            print "Total : 0"
        try:
            
            if type(self.get_children()) == type ([]):
                self = self.post_aggregate()
                 
            aggr, child, nodes, totAggr = self.intern_aggregate(self.get_children(),self.get_tree().get_dim(),level+1,threshold,total,keep_root)
            percent = aggr + self.get_value()
            percent2 = totAggr + self.get_value()
            newTotAggr = totAggr +  self.get_value()
            
            #If the node value is enough big, we keep it
            if ((100.0*percent/total >= threshold) or self.get_parent() == None)  :
                self.set_children(child)
                self.update_value(aggr)
                
                self.set_aggr_value(newTotAggr)
                
                
                new_aggr = 0
                new_child = [self]
                nodes.append(self)
            #Otherwise, we just keep the intern node and aggregate the node value to its parent thanks to the recursion
            else:
                new_aggr = aggr+self.get_value()
                new_child = child
                
            #new_aggr corresponds to the data not yet displayed and aggr_all corresponds to the total aggregation including data already displayed
            
            return new_aggr,new_child, nodes, newTotAggr
        except Exception, e:
            raise
    
    def post_aggregate(self):
        import copy
        nodes = self.preorder()
        t = Tree(self.get_tree().get_dim())
        new_nodes = []
        for n in nodes:
            nc = copy.copy(n)
            nc.set_children({})
            nc.set_parent(None)
            nc._tree = t
            nc.integrate_node()
            new_nodes.append(nc)
        
        if t.get_root().get_children() == []:
            t.get_root().set_children({})
        return t.get_root()
        
            
            
            
    def display_intern_aggregate(self,children,dim,level,threshold,total):
        if not children == None:
        
            if len(dim) == 0:
                #Final node of internal tree = node
                #This node is displayed
                return children.display_aggregate(threshold,total,level)
            else:
                d = dim[0]
                str_comb = ""
                aggr_comb = 0.0
                aggr_all_comb = 0.0

                #We explore the current dimension by extracting the different value for each direction
                if d in children.keys():
                    for direction in children[d].keys():
                        if children[d][direction] != None or children[d][direction] != {}:
                            str1, aggr1, aggr_all1 = self.display_intern_aggregate(children[d][direction],dim[1:],level,threshold,total) 
                            str_comb += str1
                            aggr_comb += aggr1
                            aggr_all_comb += aggr_all1
                    
                
                    
                return str_comb, aggr_comb,aggr_all_comb
                
        else:
            return "",0.0,0.0
            
    def display_aggregate(self,threshold,total,level=0):
        
        intern_str, aggr, aggr_all = self.display_intern_aggregate(self.get_children(),self.get_tree().get_dim(),level+1,threshold,total)
        
        percent = aggr + self.get_value()
        percent2 = aggr_all + self.get_value()
        
        #If the node value is enough big, we have to display it
        #We force also to display the root
        if (100.0*percent/total >= threshold) or self.get_parent() == None:
            toDisplay = "["
            for k in self.get_tree().get_dim():
                toDisplay = toDisplay + str(k) +"-->"+self.get_key()[k].display()+" "
            toDisplay = toDisplay + "]"
            toDisplay += " "+str(percent)+" ("+"%.2f" % (100.0*percent/total)+"% / "+"%.2f" % (100.0*percent2/total)+"%)"
        
            indent = "   "*level
            current_str = indent+toDisplay+" \n "+intern_str
            
            new_aggr = 0
            
        #Otherwise, we just display the intern node and aggregate the node value to its parent thansk to the recursion
        else:
            current_str = intern_str
            new_aggr = aggr+self.get_value()
            
        #new_aggr corresponds to the data not yet displayed and aggr_all corresponds to the total aggregation including data already displayed
        return current_str, new_aggr,aggr_all+self.get_value()
            
        
    
    @staticmethod
    def create_children_tree(dim,common_prefix,node1,node2,nodes):
       
        children = {}
        if len(dim) == 0 and len(nodes) > 1:
            raise Exception("Error in construcing internal tree of a node, after exploring all  dimensions, nodes are not separable")
            
        if len(dim) == 0:
            if len(nodes)>0:
                return nodes[0]
            else:
                return None
        else:
            d = dim[0]
            
            prefix = common_prefix[d]
    
            children[d] = {}
            
            
            #Regarding the current dimension, nodes are the same
            #and so cannot be split now, articial creation of the split
            if prefix.final_node(): # or prefix.equivalent(node1.get_key()[d]) or prefix.equivalent(node1.get_key()[d]):
                
                #sprefix = prefix.smallest_artificial_prefix()
                sprefix = prefix
                common_prefix[d] = sprefix
                
                #For the direction, keep all the nodes
                direction = sprefix.direction(node1.get_key()[d],[])
                
                children[d][direction] = Node.create_children_tree(dim[1:],common_prefix,node1,node2,nodes)
                
                """
                if direction == 0:
                    direction2 = 1
                else:
                    direction2 = 0 
                #For the artificial direction, an empty node list  is created
                children[d][direction2] = Node.create_children_tree(dim[1:],dict_dim,common_prefix,node1,node2,[])
                """
                
                
            else:

                #Standard case, each node will eb affected to the corresponding branch
                #Since the nodes may have been splitted before, it can be also an empty list
                #Node can be on the same branch if one prefix is exactly the same. In this case, nodes will be plit later and we have to keep both
                
                directions = []
                direction1 = None
                direction2 = None
                
                
                if node1 in nodes:
                    direction1 = common_prefix[d].direction(node1.get_key()[d],{})
                    directions.append(direction1)
                
                if node2 in nodes:
                    direction2 = common_prefix[d].direction(node2.get_key()[d],{})
                    directions.append(direction2)
              
                if direction1 != None and direction1 == direction2:
                    children[d][direction1] = Node.create_children_tree(dim[1:],common_prefix,node1,node2,[node1,node2])
                else:
                    if direction1 != None:
                        children[d][direction1] = Node.create_children_tree(dim[1:],common_prefix,node1,node2,[node1])
                    if direction2 != None:
                        children[d][direction2] = Node.create_children_tree(dim[1:],common_prefix,node1,node2,[node2])
               

                #Fill the remaining direction if necessary
                """
                if not 1 in directions:
                    children[d][1] = Node.create_children_tree(dim[1:],dict_dim,common_prefix,node1,node2,[])
                if not 0 in directions:
                    children[d][0] = Node.create_children_tree(dim[1:],dict_dim,common_prefix,node1,node2,[])
                """

        return children
        
    def explore_intern(self,dim,prefix):
  
        child = self.get_children()
        last_child = None
        last_direction = None
        #print "---"
        for d in dim:
            
            #print self.get_key()[d], prefix[d]
            
            if self.get_key()[d].subprefix(prefix[d]):
                #print "//",self.get_key()[d], prefix[d],child
                if not d in child.keys():
                    child[d]={}
                    
                direction = self.get_key()[d].direction(prefix[d],child[d])
                
                #print "**",direction
                
                
                last_child = child[d]
                last_direction = direction
                if direction in child[d].keys():
                    child = child[d][direction]
                else:
                    #it is required to construct the lacking subpart of the internal node representation
                    child[d][direction] = {}
                    child = child[d][direction]
                    
                    #return last_child,last_direction
                #~ if d == "dst_ip":
                    #~ print common_prefix[d],self.get_key()[d],direction
            else:
                return None
        return last_child,last_direction
            
    
    def remove_children(self,node):
        self.update_value(node.get_value())
        explore = self.explore_intern(self.get_tree().get_dim(),node.get_key())
        del explore[0][explore[1]]
        
    
    def insert_node(self,node,dim):
        """Insert a node in the current tree"""
        
        same_node = True
        final_node = True
        
        
        #compute the common prefix of each dimension
        common_prefix = {}
        
        for k in dim:
            
            #get node keys for this dimension
            val1 = self.get_key()[k]
            val2 = node.get_key()[k]
            
            #compute common prefix
            common_prefix[k] = val1.common_prefix(val2)
            
            
            #check if the prefix is exactly the same (prefix corresponds to a final node)
            if not common_prefix[k].final_node():
                same_node = False
        
            if not self.get_key()[k].final_node():
                final_node = False
        
        #~ for k,v in common_prefix.items():
            #~ print k,v
        
        if final_node:
            #If it's exactly the same node and it's not an internal, juste update the value
            if same_node:
                self.update_value(node.get_value())
            #Else, create a new branching point with the common prefix
            else:
                children = Node.create_children_tree(dim,common_prefix,self,node,[self,node])
                
                #introspection to create a node of the same type
                className = self.__class__.__name__
                branching_point = globals()[className](common_prefix,0,children,self.get_tree(),self.get_parent())
                
                #update the root tree if necessary
                if self == self.get_tree().get_root():
                    self.get_tree().set_root(branching_point)
                    
                else:
                   
                    #Order of operation is very important:
                    #1) remove old children
                    #2)create the new internal tree
                    
                    #remove the old children (now a child of the branching point)
                    explore = self.get_parent().explore_intern(dim,self.get_key())
                    explore[0][explore[1]] = None
                    
                    #update parent's children
                    #not optimized --> normally it's not necessary to recompute the internal path of the parent
                    #need to add some additional attribute to node
                    #print "la", branching_point.get_children()
                    
                    explore = self.get_parent().explore_intern(dim,branching_point.get_key())
                    #~ print self.get_parent().get_children(),Types.IntToDottedIP(branching_point.get_key()['src_ip'][1]),\
                    #~ Types.IntToDottedIP(self.get_parent().get_key()['src_ip'][1]),Types.IntToDottedIP(self.get_key()['src_ip'][1]),\
                    #~ Types.IntToDottedIP(node.get_key()['src_ip'][1])
                    
                    #print Types.subprefix(self.get_parent().get_key()['src_ip'],node.get_key()['src_ip'],'ip_addr')
                    explore[0][explore[1]] = branching_point
                    
                    
                #finalize the branching point
                node.set_parent(branching_point)
                self.set_parent(branching_point)

        
        #if the current node is an internal node
        else:
            
            #explore internal subtree to find where to put the new node
            explore = self.explore_intern(dim,node.get_key())
            """print "UUUUUU", 
            print self.display_key()
            a = explore[0][explore[1]]
            
            if a != {}:
                print "--",a.display_key()
            else:
                print explore"""
            #if the new node is not a subpart, create a branching point
            #print node.get_key()['geo1'],explore
            #~ if node.get_key()['geo1']._minval == 2 and node.get_key()['geo1']._maxval == 2 and node.get_key()['geo2']._minval ==4 and node.get_key()['geo2']._maxval == 4:
                #~ print self.get_key()['geo1'],self.get_key()['geo2'],explore
                #~ for k,v in explore[0].items():
                    #~ print "-->",k,v.get_key()['geo1'],v.get_key()['geo2']
                    
                
            if explore == None:
                #update common prefix
                #the length of the prix has to be higher because we go up in the tree
                
                children = Node.create_children_tree(dim,common_prefix,self,node,[self,node])
                
                #~ if node.get_key()['geo1']._minval == 2 and node.get_key()['geo1']._maxval == 2 and node.get_key()['geo2']._minval ==6 and node.get_key()['geo2']._maxval == 6:
                    #~ print children, node
                #~ 
                className = self.__class__.__name__
                branching_point = globals()[className](common_prefix,0,children,self.get_tree(),self.get_parent())
             
                
                if self == self.get_tree().get_root():
                    self.get_tree().set_root(branching_point)
                else:
                    #Order of operation is very important:
                    #1) remove old children
                    #2)create the new internal tree
                    
                    #remove the old children (now a child of the branching point)
                    explore = self.get_parent().explore_intern(dim,self.get_key())
                    explore[0][explore[1]] = None

                    #update parent's children
                    #not optimized --> normally it's not necessary to recompute the internal path of the parent
                    #need to add some additional attribute to node
                    #print "la", branching_point.get_children()
                    explore = self.get_parent().explore_intern(dim,branching_point.get_key())
                    explore[0][explore[1]] = branching_point
                    
                node.set_parent(branching_point)
                self.set_parent(branching_point)
                
            #Else put the new node as a children as the right place
            else:
                #if there is no previous node at this place, put the new one
                if explore[0][explore[1]] == {} or explore[0][explore[1]] == None :                   
                    explore[0][explore[1]] = node
                    node.set_parent(self)
                #else insert the new node in the subtree by a recursive call
                else:
                    explore[0][explore[1]].insert_node(node,dim)

            self.increment_uses()
            
class NumericalValueNode(Node):
    """
    Implementation of a Node class with numeric values and standard addition as aggregation
    """
    
    #Default (initial) agrgegated value has to be defined 
    def getDefaultAggr(self):
        return 0.0
       
    #Aggregation has to be defined
    def add_aggr_value(self,add):
        self.increment_uses()
        self._aggrValue += add
        
    #update the value with a new one, has to be implemented
    def update_value(self,value_to_add):
        self.increment_uses()
        self._value+=value_to_add
    
    
