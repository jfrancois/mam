import sys
import os
import re
import glob,commands
import numpy,math
from optparse import OptionParser
import copy
import time
import pickle

#sys.path.append('/home/lautaro/workspace')
#import tree
from hungarian import maxWeightMatching 
from multiAggregator import main_aggregator,build_aggregate_tree,build_aggregate_randomized_tree
from zss import test_tree
from zss.test_tree import Node
from zss import compare

from editdist import distance
class String:
    def __init__(self,val):
        self._val = val
    
    def get_val(self):
        return self._val
    
    def ___cmp__(self,val):
        return len(self._val) >= len(val.get_val())
    
    def similarity(self,val):
        import levenshtein
        return 1 - (levenshtein.levenshtein(self._val,val.get_val()) / float(max(len(self._val),len(val.get_val()))))
    
class Tree:
    def __init__(self,val,l=None,r=None,parent=None):
        self._attr = val
        self._left = l
        self._right = r
        self._parent = parent
    
    def __str__(self):
        return str(self._attr)
    
    def height(self):
        if self._left == None and self._right == None:
            return 1
        elif self._left == None and self._right != None:
            return 1 + self._right.height()
        elif self._left != None and self._right == None:
            return 1 + self._left.height()
        else:
            return 1 + max(self._left.height(),self._right.height())    
    def get_children(self):
        d=[]
        if self._left != None:
            d.append(self._left)
        if self._right != None:
            d.append(self._right)
        return d
    
    def get_root(self):
        if self._parent == None:
            return self
        else:
            return self._parent.get_root()
    
    def get_key(self):    
        return self._attr
    
    def preorder(self):
        d = [self]
        if self._left != None:
            d.extend( self._left.preorder())
        if self._right != None:
            d.extend(self._right.preorder())
        return d
    
    def insert_node(self,val):
        if val >= self._attr:
            if self._right != None:
                self._right.insert_node(val)
            else:
                t = Tree(val,None,None,self)
                self._right = t
        else:
            if self._left != None:
                self._left.insert_node(val)
            else:
                t = Tree(val,None,None,self)
                self._left = t
    
    def inorder(self):
        res = []
        if self._left == None and self._right == None:
            return [self]
        
        if self._left != None:
            l = self._left.inorder()  
            res.extend(l)
            
        res.extend([self])
         
        if self._right != None:
            r = self._right.inorder()
            res.extend(r)
        return res
    
def maxSimilarity(t1,t2):
    maxSim= 999999.0
    for u in t1.preorder():
        sim = anchoredSimilarity(u,t2.get_root())
        maxSim = min(sim,maxSim)
    print '--------------'
    for u in t2.preorder():
        sim = anchoredSimilarity(t1.get_root(),u)
        maxSim = min(sim,maxSim)
    return maxSim

def anchoredSimilarity(u,w):
    #print u,w
    if u.get_children() == [] and w.get_children() == []:
        return similarity(u,w)
    cu = u.get_children()
    cw = w.get_children()
    dsize = max(len(cu),len(cw))
    d_matrix = [[0 for v in xrange(dsize)] for l in xrange(dsize)]
    if len(d_matrix[0]) > 1 :
        for ui in xrange(len(cu)):
            for wi in xrange(len(cw)):
                dist = -1*anchoredSimilarity(cu[ui], cw[wi])
                #print dist
                d_matrix[ui][wi] = dist
        #print "s matrix",d_matrix
        assign = maxWeightMatching(d_matrix)[0]
        #print assign
        #for k in assign:
        #    print d_matrix[k][assign[k]] 
        assign = min(d_matrix[k][assign[k]] for k in assign)
        #print assign     
        
    else :
        assign = d_matrix[0][0]
    #print d_matrix , assign                 
    return similarity(u,w) + assign

def similarity(x,y):
    #return sum([1 - x.get_key()[k].similarity(y.get_key()[k]) for k in x.get_key()]) / float(3)
    import math
    if type (x.get_key()) == int:
        return 1 - (abs(x.get_key() - y.get_key()) / float(max(x.get_key(),y.get_key())))
    res = sum([x.get_key()[k].similarity(y.get_key()[k]) for k in x.get_key()]) / float(2)
    assert res <= 1.0
    return res

def f(x,y):
    #return f('',y) if x is None else f(x,'') if y is None else sum([1 - x.get_key()[k].similarity(y.get_key()[k]) for k in x.get_key()]) / float(3)
    if x is None:
        return sum([y[k].similarity(None) for k in y]) / 3 
    if y is None:
        return sum([x[k].similarity(None) for k in x]) / 3
    if x == y: return 0.0
    #for k in x:
    #    print x[k],y[k], x[k].similarity(y[k])
    return sum([x[k].similarity(y[k]) for k in x]) / 3
     
def g(x,y):
    res = f(x,y)
    try:
        assert res <= 1
    except:
        for k in x:
            print x[k], y[k] , x[k].similarity(y[k])
        print x,y,res
        raise
    return res

def benchmark_similarity(alpha,k,options,args):
    
    
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
    
    trees = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
    options.input = '../test/app_ipv4/random.%s.reverse.txt'%k
    trees1 = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
    print "Computing Similarity"
    s0 = maxSimilarity(trees[0][0],trees[-1][0])
    print "still computing"
    s1 = maxSimilarity(trees[0][0],trees1[0][0])
    print "done"
    return len(trees[0][0].preorder()),s0,s1

def T(tree):
    root = Node(tree.get_key())
    for c in tree.get_children():
        root.addkid(T(c))
    return root
'''
import random
t = Tree(random.randint(0,99))
for i in xrange(0,100):
    t.insert_node(random.randint(1,99))

f = lambda x,y: f(x,0) if y is None else f(0,y) if x is None else  (abs(x - y) / float(max(x , y))) 

test_tree = T(t)
print compare.distance(test_tree,test_tree,f)

t1 = Tree(random.randint(0,99))
for i in xrange(0,100):
    t1.insert_node(random.randint(1,99))

test_tree1 = T(t1) 
'''

def parse_options():
    lineparser = OptionParser("")
    lineparser.add_option('-i','--input', dest='input', default='../test/app_ipv4/random.0.txt',type='string',help="input file (txt flow file)", metavar="FILE")    
    lineparser.add_option('-w','--window-size', dest='window', default=5000,type='int',help="window size in seconds")    
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
    lineparser.add_option('-S','--strategy', dest='strategy', default="",type='string',help="stratrgy for selecting nodes to aggregate")
    lineparser.add_option('-m','--max-nodes', dest='max_nodes', default=99999,type='int',help="max size of tree")
    lineparser.add_option('-o','--offset', dest='offset', default=0,type='int',help="offset")
    lineparser.add_option('-b','--batch', dest='batch', default=30,type='int',help="batch")
    
    options, args = lineparser.parse_args()
    return options,args

def test_edit_distance():    
    
    options,args = parse_options()
                
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
    fout = open("similarity.edit.%s.dat"%options.offset,"w")
    upper_limit = options.batch + options.offset
    for i in xrange(0,options.batch): 
        i = i + options.offset
        lrow = "%s\t"%i
        rrow = ""   
        for alpha in [0.02, 0.5,1,2,4]:    
            options.aggregate = alpha
            options.input = '../test/app_ipv4/random.%s.txt'%i
            trees = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
            t = T(trees[0][0].get_root())
            
            options.input = '../test/app_ipv4/random.%s.reverse.txt'%i
            trees1 = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
            t1 = T(trees1[0][0].get_root())
                        
            options.input = '../test/app_ipv4/random.%s.txt'%(upper_limit-i)
            trees3 = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
            t3 = T(trees3[0][0].get_root())
            
            print "Edit Distance Based Similarity"
            s0 = compare.similarity(t,t1,g)
            s1 = compare.similarity(t,t3,g)
            lrow += "%s\t"%s0
            rrow += "%s\t"%s1
        fout.write(lrow+rrow+"\n")
    fout.close()
        
if __name__ == "__main__":
    def main():
        sys.setrecursionlimit(1000000)
        
        options,args = parse_options()
                    
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
        fout = open("similarity.2010224.test.dat","w")
        for alpa in [2]:
            options.aggregate = alpa
        
            options.input = '../test/app_ipv4/20100224/20100224.%s.txt'%i
            trees = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
            t = T(trees[0][0].get_root()) 
            
            
            options.input = '../test/app_ipv4/20100224/20100224.%s.reverse.txt'%i
            trees2 = build_aggregate_tree(options,args,fields,dim,types,dict_dim)
            t2 = T(trees2[0][0].get_root())
            
            simil = compare.similarity(t,t2,g)
            
    
        
    main() 
