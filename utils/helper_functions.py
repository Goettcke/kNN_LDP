from collections import Counter 
def key_with_max_val(d):
    """ a) create a list of the dict's keys and values; 
        b) return the key with the max value"""  

    if isinstance(d,Counter) : 
        d = dict(d)
    
    v=list(d.values())
    k=list(d.keys())
    return k[v.index(max(v))]

def key_with_min_val(d):
    """ a) create a list of the dict's keys and values; 
        b) return the key with the min value"""  

    if isinstance(d,Counter) : 
        d = dict(d)
    
    v=list(d.values())
    k=list(d.keys())
    return k[v.index(min(v))]






