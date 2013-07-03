from tree import Node,NumericalValueNode

def get_insert_path(root_node,node,dim):
        """Insert a node in the current tree"""
        
        same_node = True
        final_node = True
        
        
        #compute the common prefix of each dimension
        common_prefix = {}
        
        for k in dim:
            
            #get node keys for this dimension
            val1 = root_node.get_key()[k]
            val2 = node.get_key()[k]
            
            #compute common prefix
            common_prefix[k] = val1.common_prefix(val2)
            
            
            #check if the prefix is exactly the same (prefix corresponds to a final node)
            if not common_prefix[k].final_node():
                same_node = False
        
            if not root_node.get_key()[k].final_node():
                final_node = False
        
        #~ for k,v in common_prefix.items():
            #~ print k,v
        
        if final_node:
                return [root_node.get_parent()]
        #if the current node is an internal node
        else:
            
            #explore internal subtree to find where to put the new node
            explore = root_node.explore_intern(dim,node.get_key())
            #print explore[0][explore[1]]
            """print "UUUUUU", 
            print root_node.display_key()
            a = explore[0][explore[1]]
            
            if a != {}:
                print "--",a.display_key()
            else:
                print explore"""
            #if the new node is not a subpart, create a branching point
            #print node.get_key()['geo1'],explore
            #~ if node.get_key()['geo1']._minval == 2 and node.get_key()['geo1']._maxval == 2 and node.get_key()['geo2']._minval ==4 and node.get_key()['geo2']._maxval == 4:
                #~ print root_node.get_key()['geo1'],root_node.get_key()['geo2'],explore
                #~ for k,v in explore[0].items():
                    #~ print "-->",k,v.get_key()['geo1'],v.get_key()['geo2']
                    
                
            if explore == None:
                return [root_node]
            if explore[0][explore[1]] == {} or explore[0][explore[1]] == None :                   
                return [root_node]
            else:
                return [explore[0][explore[1]]]+ get_insert_path(explore[0][explore[1]],node,dim)



