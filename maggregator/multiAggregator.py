#!/usr/bin/python

"""
./multiAggregator.py -w 5 -r "(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d),[^,]*,[^,]*,([^,]*),([^,]*),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,([^,]*),[^,]*" -f "timestamp src_ip dst_ip value" -d "src_ip dst_ip" -d "src_ip dst_ip" -t "IPv4Address IPv4Address" -a 1 -n packets -i test > outputNewTree2
"""


import sys,re,glob,commands
import numpy,math
from optparse import OptionParser
import copy
import time
import pickle
import random
import shelve
import inspect
import os

sys.path.append(os.path.dirname(__file__)+'/features')

import feature
from feature import *
from ipv6addr import IPv6Address


#import EntropyInterval

# Import graphviz
import sys
try:
    sys.path.append('..')
    sys.path.append('/usr/lib/graphviz/python/')
    sys.path.append('/usr/lib64/graphviz/python/')
    import gv
except:
    print "No GV found"

try:
    # Import pygraph
    from pygraph.classes.graph import graph
    from pygraph.classes.digraph import digraph
    from pygraph.algorithms.searching import breadth_first_search
    from pygraph.readwrite.dot import write
    
except:
    print "No pygraph found"

        
from tree import Tree,Node,NumericalValueNode
#,list_node


VALUE="value"



def test_types():

    
    if IPv4Address.DottedIPToInt("108.64.77.102") == 1816153446:
        print "test_types DottedIPToInt success"
    else:
        print "test_types DottedIPToInt ERROR"
    
    if IPv4Address.IntToDottedIP(1816153446) == "108.64.77.102":
        print "test_types IntToDottedIP success"
    else:
        print "test_types IntToDottedIP ERROR"
        
    a = IPv4Address ("108.64.77.102",32,True)
    b = IPv4Address.create_final_value ("108.64.88.88")
    c = a.common_prefix(b)
   
    
    if c.display() == "108.64.64.0/19":
        print "test_types common_prefix with ip_addr success"
    else:
        print "test_types common_prefix with ip_addr ERROR"
        
        
    if a.final_node() == True:
        print "test_types final_node with ip_addr success"
    else:
        print "test_types final_node with ip_addr ERROR"
        
        
    pref = IPv4Address("108.64.0.0",16)
    d = IPv4Address ("108.64.135.32",32)
    e = IPv4Address ("108.64.96.32",24)
    if pref.direction(d) == 1 and pref.direction(e) ==0:
        print "test_types direction with ip_addr success"
    else:
        print "test_types direction with ip_addr ERROR"
    
    if b.smallest_artificial_prefix().display()  == "108.64.88.88/31":
        print "test_types smallest_artificial_prefix with ip_addr success"
    else:
        print "test_types smallest_artificial_prefix with ip_addr ERROR"
   
    if pref.subprefix(a) == True:
        print "test_types subprefix with ip_addr success"
    else:
        print "test_types subprefix with ip_addr ERROR"
        

      
        
def test_node():
    
    def test_preorder_iterator():
        tree = Tree('src_ip dst_ip')
        create_node(2,1,tree)
        create_node(2,2,tree)
        create_node(1,2,tree)
        create_node(3,1,tree)
        create_node(4,1,tree)
        print tree.get_root.preorder()
        return tree
    
        
        
    def create_node_prefix(src,dst,src_size,dst_size,tree):
        key = {}
        a = IPv4Address(src,src_size)
        b = IPv4Address(dst,dst_size)
        key["src_ip"] = a
        key["dst_ip"] = b
        node1 = NumericalValueNode(key,10,None,tree)
        return node1
        
    def create_detached_node(src,dst,tree):
        key = {}
        a = IPv4Address(src,32)
        b = IPv4Address(dst,32)
        key["src_ip"] = a
        key["dst_ip"] = b
        node1 = NumericalValueNode(key,10,None,tree)
        return node1
    
    
    
    def create_node(src,dst,tree):
        key = {}
        a = IPv4Address(src,32)
        b = IPv4Address(dst,32)
        key["src_ip"] = a
        key["dst_ip"] = b
        node1 = NumericalValueNode(key,10,None,tree)
        node1.integrate_node()
        return node1
    
    
    def check_tree(tree):
        nodePP = create_node_prefix("0.0.0.0","0.0.0.0",0,0,tree)
        nodeCH = create_node_prefix("108.64.64.0","108.96.64.0",19,19,tree)
        nodeJL = create_node_prefix("108.64.88.0","108.96.77.88",24,31,tree)
        
        
        if tree.get_root().equivalent(nodePP,tree.get_dim()):
            print "test tree root success"
        else:
            print "test tree root ERROR"
            return False
            
        listNone = []
        try:
            listNone.append(tree.get_root().get_children()['src_ip'][0]['dst_ip'][1])     
        except KeyError:
            listNone.append(None)
            
        try:
            listNone.append(tree.get_root().get_children()['src_ip'][1]['dst_ip'][0])     
        except KeyError:
            listNone.append(None)
        
        ch = tree.get_root().get_children()['src_ip'][0]['dst_ip'][0]
        mn = tree.get_root().get_children()['src_ip'][1]['dst_ip'][1]
        
        af = ch.get_children()['src_ip'][0]['dst_ip'][0]
        ag = ch.get_children()['src_ip'][0]['dst_ip'][1]
        
        jl = ch.get_children()['src_ip'][1]['dst_ip'][0]
        bg = ch.get_children()['src_ip'][1]['dst_ip'][1]
        

        bf = jl.get_children()['src_ip'][0]['dst_ip'][0]
        i_f = jl.get_children()['src_ip'][1]['dst_ip'][0]
        
        try:
            listNone.append(jl.get_children()['src_ip'][0]['dst_ip'][1])     
        except KeyError:
            listNone.append(None)
        
        try:
            listNone.append(jl.get_children()['src_ip'][1]['dst_ip'][1])     
        except KeyError:
            listNone.append(None)
            
        ok = True
        for e in listNone:
            if e!=None:
                ok = False
        if ok:
            print "test tree empty_node success"
        else:
            print "test tree empty_node ERROR"
            return False
        
        nodeAF = create_detached_node("108.64.77.102","108.96.77.88",tree)
        nodeBG = create_detached_node("108.64.88.102","108.96.88.88",tree)
        nodeAG = create_detached_node("108.64.77.102","108.96.88.88",tree)
        nodeBF = create_detached_node("108.64.88.102","108.96.77.88",tree)
        nodeIF = create_detached_node("108.64.88.130","108.96.77.88",tree)
        nodeMN = create_detached_node("202.102.10.10","210.110.0.0",tree)
        
        ok = True
        if not nodeAF.equivalent(af,tree.get_dim()):
            ok = False
        if not nodeAG.equivalent(ag,tree.get_dim()):
            ok = False
        if not nodeBF.equivalent(bf,tree.get_dim()):
            ok = False
        if not nodeIF.equivalent(i_f,tree.get_dim()):
            ok = False
        if not nodeMN.equivalent(mn,tree.get_dim()):
            ok = False
        if not nodeBG.equivalent(bg,tree.get_dim()):
            ok = False
        
        if ok:
            print "test tree leaf nodes success"
        else:
            print "test tree leaf ERROR"
            return False
    
        ok = True
        if not nodeCH.equivalent(ch,tree.get_dim()):
            ok = False
        if not nodeJL.equivalent(jl,tree.get_dim()):
            ok = False
        
        if ok:
            print "test tree internal nodes success"
        else:
            print "test tree internal nodes ERROR"
            return False
            
        ok = True
        if not (tree.get_root().get_value() == 0 and ch.get_value() == 0 and jl.get_value() == 0):
            ok = False
        
        if not (mn.get_value() == 10 and af.get_value() == 10 and ag.get_value() == 20 and bg.get_value() == 10\
        and i_f.get_value() == 10 and bf.get_value() == 10):
            ok = False
            
        if ok:
            print "test tree value success"
        else:
            print "test tree value nodes ERROR"
            return False
            
        return True
            
    def generate_posssibilities(p,E):
        if p==1:
            return [[x] for x in E] #cas ou p=1
        else:
            R=[]
            for x in E:
                F=E[:] # recopier E
                F.remove(x) # enlever x
                PGI=generate_posssibilities(p-1,F) # appel recursif
                Cx=PGI[:] # recopie du resultat
                for A in Cx:
                    A.append(x)# recombiner avec x tous les elements
                R+=Cx # Ajouter les resultats obtenus
        return R
            

    
    key = {}
            
    a = IPv4Address("108.64.77.102",32)
    b = IPv4Address("108.96.77.88",32)
    key["src_ip"] = a
    key["dst_ip"] = b
    
    node1 = NumericalValueNode(key,10,[])
    
    key = {}
    c = IPv4Address("108.64.88.102",32)
    d = IPv4Address("108.96.88.88",32)
    key["src_ip"] = c
    key["dst_ip"] = d
    
    node2 = NumericalValueNode(key,20,[])
    
    dict_dim={"src_ip":"ip_addr","dst_ip":"ip_addr"}
    
    common_prefix={"src_ip":a.common_prefix(c),"dst_ip":b.common_prefix(d)}
        
    dim = ["src_ip","dst_ip"]
    child = Node.create_children_tree(dim,common_prefix,node1,node2,[node1,node2])

    
    if IPv4Address.IntToDottedIP(common_prefix["src_ip"].get_prefix()) == "108.64.64.0" and common_prefix["src_ip"].get_prefix_len() == 19 and IPv4Address.IntToDottedIP(common_prefix["dst_ip"].get_prefix()) == "108.96.64.0" and common_prefix["dst_ip"].get_prefix_len() == 19:
        print "test nodes common_prefix success"
    else:
        print "test nodes common_prefix ERROR"
        
   
    if child['src_ip'][0]['dst_ip'][0] == node1 and not 1 in child['src_ip'][0]['dst_ip'].keys() and not 0 in child['src_ip'][1]['dst_ip'].keys() and child['src_ip'][1]['dst_ip'][1] == node2:
        print "test nodes create_children success"
    else:
        print "test nodes create_children ERROR"
        

    key = {}
    c = IPv4Address("108.64.77.102",32)
    d = IPv4Address("108.96.88.88",32)
    key["src_ip"] = c
    key["dst_ip"] = d
    
    tt = node1.__class__.__name__

    node2 = globals()[tt](key,20,[])
    
    common_prefix={"src_ip":a.common_prefix(c),"dst_ip":b.common_prefix(d)}
    
    dim = ["src_ip","dst_ip"]
    child = Node.create_children_tree(dim,common_prefix,node1,node2,[node1,node2])

    
    if IPv4Address.IntToDottedIP(common_prefix["src_ip"].get_prefix()) == "108.64.77.102" and common_prefix["src_ip"].get_prefix_len() == 31 and IPv4Address.IntToDottedIP(common_prefix["dst_ip"].get_prefix()) == "108.96.64.0" and common_prefix["dst_ip"].get_prefix_len() == 19:
        print "test nodes common_prefix with artificial split success"
    else:
        print "test nodes common_prefix ERROR"
    
  

    #if child['src_ip'][0]['dst_ip'][0] == node1 and not 1 in child['src_ip'].keys() and child['src_ip'][0]['dst_ip'][1] == node2:
    #    print "test nodes create_children 2 success"
    #else:
    #    print "test nodes create_children 2 ERROR"
    
    tree = Tree(dim)
    if tree.is_empty() == True:
        print "test tree is_empty 1 success"
    else:
        print "test tree is_empty 1 ERROR"
        
    
    nodeAF = create_node("108.64.77.102","108.96.77.88",tree)
    key = {}
    
    if tree.is_empty() == False:
        print "test tree is_empty 2 success"
    else:
        print "test tree is_empty 2 ERROR"
    
    
    node2 = create_node("108.64.77.102","108.96.77.88",tree)

    tree = Tree(dim)
    
    nodeBG = create_node("108.64.88.102","108.96.88.88",tree)
    nodeAF = create_node("108.64.77.102","108.96.77.88",tree)
    nodeAG = create_node("108.64.77.102","108.96.88.88",tree)
    nodeAG2 = create_node("108.64.77.102","108.96.88.88",tree)
    nodeBF = create_node("108.64.88.102","108.96.77.88",tree)
    nodeIF = create_node("108.64.88.130","108.96.77.88",tree)
    """
    explore = tree.get_root().explore_intern(dim,dict_dim,IPv4Address(32,"108.64.88.130"))
    print explore[0]
    print explore[1]
    """

    nodeMN = create_node("202.102.10.10","210.110.0.0",tree)
    print tree.display()
    check_tree(tree)
    
    
    
    
    tree = Tree(dim)
    nodeAF = create_node("108.64.77.102","108.96.77.88",tree)
    nodeBG = create_node("108.64.88.102","108.96.88.88",tree)
    nodeAG = create_node("108.64.77.102","108.96.88.88",tree)
    nodeBF = create_node("108.64.88.102","108.96.77.88",tree)
    nodeIF = create_node("108.64.88.130","108.96.77.88",tree)
    nodeMN = create_node("202.102.10.10","210.110.0.0",tree)
    nodeAG.get_parent().remove_children(nodeAG)
    
    
    if not 1 in nodeAG.get_parent().get_children()['src_ip'][0]['dst_ip'].keys() and nodeAG.get_parent().get_value() == 10:
        print "Test tree remove success"
    else:
        print "Test tree remove ERROR"
    print tree.get_root.preorder()
    print tree.display()
    
    #~ list_node_to_create=[("108.64.77.102","108.96.77.88"),("108.64.88.102","108.96.88.88"),("108.64.77.102","108.96.88.88"),\
    #~ ("108.64.88.102","108.96.77.88"),("108.64.88.130","108.96.77.88"),("202.102.10.10","210.110.0.0")]
    #~ 
    #~ creators =  generate_posssibilities(len(list_node_to_create),copy.copy(list_node_to_create))
    #~ 
    #~ for i in range(len(creators)):
        #~ print "test creation",i+1,"/",len(creators)
        #~ creator = creators[i]
        #~ tree = Tree(dim,dict_dim)
        #~ for c in creator:
            #~ create_node(c[0],c[1],tree)
        #~ if not check_tree(tree):
            #~ print creator
            #~ print tree.display()
            #~ break
        #~ #check_tree(tree)

    
def test(): 

    test_types()
    test_node()

def update_tree(tree,dict_fields,dict_dim,aggr):
    
    
    #Create the key corresponding to the entry
    key = {}
    for k,v in dict_fields.items():
        if k in dict_dim.keys():
  
            key[k] = globals()[dict_dim[k]].create_final_value(v)
            
    #aggregate here in order to keep a fixed size tree
    #TODO: Aggrate based on LRU
    
    node = globals()[aggr](key,float(dict_fields[VALUE]),{},tree)
    #node.integrate_node()
    if tree.get_root() != None:
        tree.get_root().insert_node(node,tree.get_dim())
    else:
        node.integrate_node()
    #print node   
    return node
    
def aggregate_LRU(tree,max_nodes,alpha,age=-1):
        import copy
        nodes = tree.preorder()
        nodes = sorted(nodes,key=lambda x: x.get_uses())[0:100]
        nodes = sorted(nodes,key=lambda x: x.get_age(),reverse=True)
        candidate = nodes[0]
        nodes = nodes[1:]
        
        #go 2 levels up....
        try:
            c_root = candidate.get_parent().get_parent()
        except:
            try:
                c_root = candidate.get_parent()
            except:
                c_root = candidate
            
        count = sum((n.get_value() for n in c_root.preorder()))
        #print len(c_root.preorder())
        while len(nodes) > 0 and count <= 0 :
            candidate = nodes[0]
            nodes = nodes[1:]
            #go 2 levels up....
            c_root = candidate.get_parent().get_parent()
            if c_root == None:
                c_root = candidate.get_parent()
            if c_root == None:
                c_root = candidate
            count = sum((n.get_value() for n in c_root.preorder()))
            
        c_root.aggregate(alpha,count,0)
        #print len(c_root.preorder())
        return c_root.post_aggregate()
            
        
def build_LRU_aggregate_tree(options,args,fields,dim,types,dict_dim):
    def f(x,y):
        new_node = aggregate_LRU(x,options.max_nodes,options.aggregate)
        nodes = x.preorder()
        for n in nodes:
            if n.get_key() == new_node.get_key():
                if new_node.get_parent() !=None:
                    new_node.set_parent(n.get_parent())
                    new_node.set_tree(x)
                    break
        return x.get_root()
        
    return build_aggregate_tree(options,args,fields,dim,types,dict_dim,f,False,True)
        
def build_root_aggregate_tree(options,args,fields,dim,types,dict_dim):
    def f(tree,tc):
        tree.aggregate(options.aggregate,tc)
        return tree.get_root().post_aggregate()    
    return build_aggregate_tree(options,args,fields,dim,types,dict_dim,f)

def benchmark_aggregation(options,args,fields,dim,types,dict_dim, otfa = lambda x: x.get_root()):
    
    tree_src = None
    tree_dst = None
   
    list_res = []
    list_window = []
    tree = None
    f = open(options.input) 
    
    total_count = 0.0
    current_window = 0
    tree = Tree(dim)
    k = 0
    for line in f:
        find = re.search(options.reg_exp,line)
        if find:
            dict_fields = {}
            for i in range(len(fields)):
                dict_fields[fields[i]] = find.group(i+1)
            #print dict_fields
            try:
                sec = time.mktime(time.strptime(dict_fields["timestamp"],"%Y-%m-%d %H:%M:%S"))
            except:
                sec = int(dict_fields["timestamp"])

            
            
            list_window.append(current_window)
            
            try:    
                update_tree(tree,dict_fields,dict_dim,options.type_aggr)
            except:
                tree.set_root(tree.get_root().post_aggregate())
                update_tree(tree,dict_fields,dict_dim,options.type_aggr)
            total_nodes = len(tree.get_root().preorder())
            if total_nodes > options.max_nodes:
                tree.set_root(otfa(tree,total_count))
                tree.set_root(tree.get_root().post_aggregate())
                #aggregate_LRU(tree,options.max_nodes,options.aggregate,total_count)
            
            #print tree.get_root().preorder()
            #tree.increase_age_tree()
            
            total_count+= float(dict_fields[VALUE])
            
            map(lambda x: x.increase_age(),tree.get_root().preorder())
        
            
        
        k=k+1
        
        if options.max_lines > 0 and options.max_lines < k :
            break    
    
    if tree.get_root() != None:
        list_res.append((tree,total_count))
    
            
    pretotal_nodes_before_aggregation = len(tree.get_root().preorder())
    tree.aggregate(options.aggregate,total_count)
       
            
    print "Total nodes before pre order aggregation %s"%pretotal_nodes_before_aggregation
    print "Total nodes after aggregation %s"%len(tree.get_root().preorder())
        
            
    #print [(n.get_value(),n._age,n._uses) for n in tree.get_root().preorder()]
    
    
    #print list_window
def build_aggregate_randomized_tree(options,args,fields,dim,types,dict_dim):
    return build_aggregate_tree(options,args,fields,dim,types,dict_dim, otfa = lambda x,y: x.get_root(),randomize=True)

def build_aggregate_tree(options,args,fields,dim,types,dict_dim, otfa = lambda x,y: x.get_root(),randomize=False,no_final_aggregation=False):
    
    tree_src = None
    tree_dst = None
   
    list_res = []
    list_window = []
    tree = None
    f = open(options.input) 
    lines = [ l for l in f]
    f.close()
    
    if randomize: random.shuffle(lines)
    
    total_count = 0.0
    current_window = 0
    
    for line in lines:
   
        find = re.search(options.reg_exp,line)
        if find:
            dict_fields = {}
            for i in range(len(fields)):
                dict_fields[fields[i]] = find.group(i+1)
            #print dict_fields
            try:
                #    print dict_fields["timestamp"]
                sec = time.mktime(time.strptime(dict_fields["timestamp"],"%Y-%m-%d %H:%M:%S"))
            except:
                sec = int(dict_fields["timestamp"])

            if sec >= current_window + options.window: 
                if tree != None:
                    list_res.append((tree,total_count))
                    tree = Tree(dim)
                    current_window = current_window + options.window
                    
                    while sec>= current_window + options.window:
                        list_res.append((None,0.0))
                        list_window.append(current_window)
                        current_window = current_window + options.window
                    
                else:
                    tree = Tree(dim)
                    current_window = sec
                total_count = 0.0
                
                list_window.append(current_window)
                
            try:    
                update_tree(tree,dict_fields,dict_dim,options.type_aggr)
            except Exception, e:
                print e
                raise
                tree.set_root(tree.get_root().post_aggregate())
                update_tree(tree,dict_fields,dict_dim,options.type_aggr)
            total_nodes = len(tree.get_root().preorder())
            if total_nodes > options.max_nodes:
                tree.set_root(otfa(tree,total_count))
                tree.set_root(tree.get_root().post_aggregate())
                #aggregate_LRU(tree,options.max_nodes,options.aggregate,total_count)
            
            #print tree.get_root().preorder()
            #tree.increase_age_tree()
            
            total_count+= float(dict_fields[VALUE])
            
            map(lambda x: x.increase_age(),tree.get_root().preorder())
    if tree.get_root() != None:
        list_res.append((tree,total_count))
    
    
    
    #sys.exit()
    i = 0
    list_files = []
    if len(options.strategy) > 0:
        sname = "_%s" % options.strategy
    else:
        sname = ""
    storage = shelve.open("chunkstrees.dat")
    for (res_t,res_c) in list_res:            
        print "-------------------------------"
        print "Total = ",res_c
        if res_t !=None:
            
            
            #print res_t.display()
            
            #print res_t.display_aggregate(options.aggregate,res_c)
            
            #res_t.display_aggregate(options.aggregate,res_c)
            k = options.input.split("/")[-1] + ".%s_%s_%s"%(i,options.aggregate,sname)
            storage[k]= { 'tree': res_t }  
            pretotal_nodes_before_aggregation = len(tree.get_root().preorder())
            if not no_final_aggregation:
                res_t.aggregate(options.aggregate,res_c)
            if options.strategy != "":
                res_t.set_root(res_t.get_root().post_aggregate())
                res_t.aggregate(options.aggregate,res_c)
            
                
            
            print res_t.display_preaggregate(res_c)
            fwrite = open("%s.%s.dot"%(options.input.replace(".txt",''),i),"w")
            fwrite.write(res_t.dot_preaggregate(res_c))
            fwrite.close()
            storage[k]['atree'] = res_t
            if "Range" in options.types: 
                try:
                    
                    fwrite = open("%s.%s.map.html"%(options.input.replace(".txt",''),i),"w")
                    
                    squares = res_t.gmap_preaggregate(res_c)
                    res = gmap_template() % squares
                    fwrite.write(res)
                    fwrite.close()
                    
                    list_files.append("%s.%s.map.html"%(options.input.replace(".txt",''),i))
                except Exception,e:
                    print e,"cannot display google map"
            else:
                    
                try:
                    dot_file = "%s.%s.dot"%(options.input.replace(".txt",''),i)
                    print dot_file
                    gvv = gv.read(dot_file)
                    gv.layout(gvv,'dot')
                    new_file_gv = "%s.%s_%s_%s.png"%(options.input.replace(".txt",''),i,options.aggregate,sname)
                  
                    list_files.append(new_file_gv)
                    
                    gv.render(gvv,'png',new_file_gv)
                except Exception, e:
                    print e
                    print "No Rendering"    
            i=i+1
            
            print "Total nodes before pre order aggregation %s"%pretotal_nodes_before_aggregation
            print "Total nodes after aggregation %s"%len(res_t.get_root().preorder())
            
            #fwrite = open("gmap.dat","w")
            #fwrite.write(res_t.gmap_preaggregate(res_c))
            #fwrite.close()

        #print tree.display_aggregate(options.aggregate,total_count)        
        
            #res_t.aggregate(options.aggregate,res_c)        
            #print res_t.display_preaggregate(res_c)

        print "-------------------------------"
    storage.close()    
    return (list_res,list_files)        
    #print [(n.get_value(),n._age,n._uses) for n in tree.get_root().preorder()]
    
    
    #print list_window
def gmap_template():
    return '''<!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
    <title>Google Maps JavaScript API v3 Example: Polygon Simple</title>
    <link href="http://code.google.com/apis/maps/documentation/javascript/examples/default.css" rel="stylesheet" type="text/css" />
    <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?sensor=false"></script>
    <script type="text/javascript">
    var map;
    var infowindow;
      function initialize() {
        var myLatLng = new google.maps.LatLng(49.4958000183, 5.98059988022);
        var myOptions = {
          zoom: 5,
          center: myLatLng,
          mapTypeId: google.maps.MapTypeId.TERRAIN
        };
    
        var bermudaTriangle;
    
        map = new google.maps.Map(document.getElementById("map_canvas"),
            myOptions);
     %s
     
     
        
    infowindow = new google.maps.InfoWindow();
     
     
      }
      
      function showArrays(event) {
    
      // Since this Polygon only has one path, we can call getPath()
      // to return the MVCArray of LatLngs
      var vertices = this.getPath();
    
      var contentString = "<b>Generated by Multidimensional Aggregator</b><br />";
      contentString += "Clicked Location: <br />" + event.latLng.lat() + "," + event.latLng.lng() + "<br />";
    
      // Iterate over the vertices.
      for (var i =0; i < vertices.length; i++) {
        var xy = vertices.getAt(i);
        contentString += "<br />" + "Coordinate: " + i + "<br />" + xy.lat() +"," + xy.lng();
      }
    
      // Replace our Info Window's content and position
      infowindow.setContent(contentString);
      infowindow.setPosition(event.latLng);
    
      infowindow.open(map);
    }
    
    function get_random_color() {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.round(Math.random() * 15)];
        }
        return color;
    }
    
    
    </script>
    </head>
    <body onload="initialize()">
      <div id="map_canvas"></div>
    </body>
    
    </html>'''        

def split_input(options,args,fields,dim,types,dict_dim, otfa = lambda x: x.get_root(),randomize=False,no_final_aggregation=False):
    
    tree = None
    f = open(options.input) 
    lines = [ l for l in f]
    f.close()
    
    if randomize: random.shuffle(lines)
    
    total_count = 0.0
    current_window = 0
    cuts = []
    for line in lines:
        find = re.search(options.reg_exp,line)
        if find:
            dict_fields = {}
            for i in range(len(fields)):
                dict_fields[fields[i]] = find.group(i+1)

            try:
                sec = time.mktime(time.strptime(dict_fields["timestamp"],"%Y-%m-%d %H:%M:%S"))
            except:
                sec = int(dict_fields["timestamp"])

            if sec >= current_window + options.window: 
                if tree != None:
                    cuts.append(lines.index(line))
                    tree = Tree(dim)
                    current_window = current_window + options.window
                    
                    while sec>= current_window + options.window:
                        current_window = current_window + options.window
                    
                else:
                    tree = Tree(dim)
                    current_window = sec
                total_count = 0.0
                
    print cuts                
    cuts = [0] + cuts
    for i in xrange(0,len(cuts)-1):
        f = open(options.input.replace(".txt",".%s.txt" % i),'w')
        for j in lines[cuts[i]:cuts[i+1]]:
            f.write(j)
        f.close()
            
        
def main_aggregator(lineparser):
    options, args = lineparser.parse_args()
    
    fields = options.fields.split(" ")
    dim = options.dim.split(" ")
    types = options.types.split(" ")
    
    
    #test()
    
    #For csv
    #"(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d),[^,]*,[^,]*,([^,]*),([^,]*),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,([^,]*)"
 
    dict_dim = {}
    
    if len(dim) != len(types):
        raise Exception("The number of defined dimensions and types has to be equal")
    else:
        for i in range(len(dim)):
            dict_dim[dim[i]] = types[i]

            
    res = None
    
    if len(options.strategy) > 0 :         
        method_name = "build%s_aggregate_tree" % ("_"+options.strategy)
        try:
            fun = getattr(sys.modules[__name__],method_name)
        except:
            raise Exception("Strategy not implemented %s"%options.strategy)
        res = fun(options,args,fields,dim,types,dict_dim)
    
    else:
        res = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
    return res


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
   
    lineparser = OptionParser("")
    lineparser.add_option('-i','--input', dest='input', default="input.txt",type='string',help="input file (txt flow file)", metavar="FILE")    
    lineparser.add_option('-w','--window-size', dest='window', default=10,type='int',help="window size in seconds")    
    lineparser.add_option('-r','--reg-exp', dest='reg_exp', default="",type='string',help="regular expression to extract flow information")    
    lineparser.add_option('-f','--fields', dest='fields', default="src_ip",type='string',help="fields naming corresponding to the regular expression, have to be split by a space character and HAS TO INCLUDE value and timestamp")    
    lineparser.add_option('-d','--dimensions', dest='dim', default="src_ip",type='string',help="dimension to use for the radix tree, have to be split by a space character and correspond to the field naming")    
    lineparser.add_option('-t','--type-dimension', dest='types', default="ip_addr",type='string',help="types of dimension")    
    lineparser.add_option('-c','--cut', dest='cut', default=0.02,type='float',help="threshold (%) under which removing a node is not allowed during the construction(it's include the parents values)")    
    lineparser.add_option('-a','--aggregate', dest='aggregate', default=0.02,type='float',help="threshold (%) for the aggregation")    
    lineparser.add_option('-l','--log-file', dest='log',default="log.att",type='string',help="log file containing the attacks", metavar="FILE")    
    lineparser.add_option('-s','--split', dest='split', default=20,type='float',help="percentage of data used for training")
    lineparser.add_option('-g','--type-aggregation', dest='type_aggr', default="NumericalValueNode",type='string',help="type of the aggregation for nodes")   
    
    lineparser.add_option('-n','--name', dest='namefile', default="bytes",type='string',help="suffix for name of file results")    
    lineparser.add_option('-S','--strategy', dest='strategy', default="",type='string',help="strategy for selecting nodes to aggregate")
    lineparser.add_option('-m','--max-nodes', dest='max_nodes', default=99999,type='int',help="max size of tree")
    
    main_aggregator(lineparser)
    
