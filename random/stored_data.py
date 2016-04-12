import pandas as pd
import numpy as np
import os
import get_symbols

def get_data(path):
    if os.path.exists(path)==False:
        print('no path')
        return 'nada'
    data = pd.read_pickle(path)
    return data

def get_top_strats(symbols, path, N):
    rets = dict()
    for symbol in symbols:
        path_  = ''.join((path, symbol))
        data = get_data(path_)
        #if data == 'nada':
         #   pass
        
        ret = np.prod(data+1)
        rets[symbol] = ret
        
    topN = sorted(rets, key=rets.get, reverse=True)[:N]
    ls = {x:(rets[x]) for x in topN}
    return ls

def get_top_strats_until(symbols, path, N, until):
    rets = dict()
    for symbol in symbols:
        path_  = ''.join((path, symbol))
        data = get_data(path_)
        #if data == 'nada':
         #   pass
       
        try:   
       	    ret = np.prod(data[:until]+1)
            rets[symbol] = ret
        except:
            pass
    topN = sorted(rets, key=rets.get, reverse=True)[:N]
    ls = {x:(rets[x]) for x in topN}
    return ls

def get_top_strats_after(symbols, path, N, after):
    rets = dict()
    for symbol in symbols:
        path_  = ''.join((path, symbol))
        data = get_data(path_)
        #if data == 'nada':
         #   pass
        try:
            ret = np.prod(data[after:]+1)
            rets[symbol] = ret
        except:
            pass
    topN = sorted(rets, key=rets.get, reverse=True)[:N]
    ls = {x:(rets[x]) for x in topN}
    return ls

def get_top_strats2(directory_, N):
    path = ''.join(('../output/', directory_))
    symbols  =get_symbols.main()
    rets = dict()
    rets2 = dict()
    for symbol in symbols:
        path_  = ''.join((path, symbol))
        data = get_data(path_)
        #if data == 'nada':
         #   pass
        
        ret = np.prod(data[:'2013']+1)
        rets[symbol] = ret
        
        ret2 = np.prod(data['2014':]+1)
        rets2[symbol] = ret
        
    topN = sorted(rets, key=rets.get, reverse=True)[:N]
    ls = {x:(rets2[x]) for x in topN}
    return ls


def check_performance( directory_= 'curve_oldfart_50_1000_200/'):
    l=get_symbols.main()
    dirr = ''.join(('../output/', directory_))
    top = get_top_strats_until(l, dirr, 50, '2014')
    ttop = get_top_strats_after(top, directory_, 50, '2015')
    before_avg = np.nanmean(list(top.values()))
    after_avg = np.nanmean(list(ttop.values()))
    
    print(before_avg)
    print(before_avg**(1/4))
    print(after_avg)
    
    
    
def full_performance(symbols, path, N):
    rets = dict()
    for symbol in symbols:
        path_  = ''.join((path, symbol))
        data = get_data(path_)
        #if data == 'nada':
         #   pass
        
        ret = np.prod(data+1)
        rets[symbol] = ret
        
    ls = {x:(rets[x]) for x in symbols}
    avg = np.nanmean(list(ls.values()))
    
    return ls, avg



if __name__=='__main__':
    import sys
    get_top_strats2(sys.argv[1], 20)
'''
    try: 
        get_top_strats2(sys.argv[1], 20)   
        #check_performance(sys.argv[1])
    except: 
        check_performance()
    symbols = get_symbols.main()
    directory_= 'curve_youngbuck_50_1000_200/'
    path = ''.join(('../output/', directory_))
    N=50
    full_performance(symbols, path, N)
'''
