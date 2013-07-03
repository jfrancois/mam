import math
import ipath
import shelve
import tree
import sys

def imatrix(nodes_list):
    insert_matrix = {}
    for t in nodes_list:
        insert_matrix[nodes_list.index(t)] = []
        for n in t:
            insert_sequence = []
            for r in [k[0] for k in nodes_list]:
                insert_sequence.append(ipath.get_insert_path(r,n,t[0].get_tree().get_dim()))
            insert_matrix[nodes_list.index(t)].append(insert_sequence)
    return insert_matrix


def stability_function(i,j,d):
    return i.get_key()[d].stability(j.get_key()[d])
    
def ip_stability(i,j):
    iip = i.get_key()['src_ip']._prefix_len
    jip = j.get_key()['src_ip']._prefix_len
    return 1 - (2**math.fabs(iip-jip)/2**32)

def domain_stability(i,j,d='sip'):
    i_dom = i.get_key()[d]._domain
    j_dom = j.get_key()[d]._domain
    clean_terminals = lambda x: [i for i in x.split(".") if i not in [".","$","ROOT"] and len(i) > 0]    
    union = list(set(clean_terminals(i_dom) + clean_terminals(j_dom)))
    inter = list(set(clean_terminals(i_dom)) & set(clean_terminals(j_dom)))
    return 0.0 if len(union)  == 0 else float(len(inter))/float(len(union))

def stability_index_md(i,j,dim):
    res = 0.0    
    if i and j:
        m = math.fabs(i._value - j._value) / max(i._value,j._value) if max(i._value,j._value) > 0 else 0
        res = sum([i.get_key()[d].similarity(j.get_key()[d]) for d in i.get_key().keys()]) + m / float(len(d)+1)    
    return res
    
def stability_index(i,j):
    '''m = math.fabs(i._value - j._value) / max(i._value,j._value) if max(i._value,j._value) > 0 else 0  
    res = 0.3 * ip_stability(i,j) + 0.3*domain_stability(i,j)+0.3*m
    return float("%.4f"%res)'''
    res = 0.0    
    if i and j:    
        m = math.fabs(i._value - j._value) / max(i._value,j._value) if max(i._value,j._value) > 0 else 0
        st_list = [i.get_key()[d].similarity(j.get_key()[d]) for d in i.get_key().keys()]
        #print 'stlist',len(st_list)
        res = (sum(st_list) + m) / float(len(i.get_key())+1)
        #print res
    return res

def get_st(nodes_list,insert_matrix):
    max_stable_nodes = []
    stability = {}
    for i in xrange(0,len(nodes_list)):
        stability[i] = {}
        for j in xrange(0,len(nodes_list[i])):
                stability[i][j] = [max([stability_index(nodes_list[i][j],y) for y in x]) for x in insert_matrix[i][j] ]
    #st = [stability[i][j] for i in stability.keys() for j in stability[i].keys()]
    return stability

def get_trees_stability(input_file,alpha):
    import tree
    ctrees = shelve.open("siptest.dat")
    tree_keys = sorted(filter(lambda x: "%s"%input_file in x and "_%s."%alpha in x ,ctrees.keys()),key=lambda x: int(x.split(".")[2].split("_")[0]))
    nodes_list = [ctrees[k]['tree'].preorder() for k in tree_keys]
    im = imatrix(nodes_list)
    st = get_st(nodes_list,im)
    return st
