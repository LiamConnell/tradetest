import random
import pandas as pd
import numpy as np
from yahoo_finance import Share
import matplotlib
import datetime
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib
import sys
sys.path.append('../')
import get_symbols
import os
from multiprocessing import Process, Pool

from trade_logic import *



def get_sweetspot(data, logic, wf_window):
    
    cs=[]
    eqs=[]
    for x in range(10):
        c = .15*x+1
                #thresh = c*np.std(data['resid'])
        if logic=='oldfart':
            data['stratret1'], pp = trade_logic(data, c)
        if logic=='youngbuck':
            data['stratret1'], pp = trade_logic2(data, c)
                
        eqcurve = np.cumprod(3*data.stratret1+1)
        cs.append(c)
        eqs.append(eqcurve[-wf_window])
    data  = data.iloc[-wf_window:]#tail(wf_window)      
    if max(eqs)<1:
        print('nein!')
        data['stratret']= data['pos'] =pd.Series(np.zeros(len(data.index)), index=data.index)
              #  return 
    else:
        c = cs[np.argmax(eqs)]
        print(c)
                #c=2
        if logic=='oldfart':
            data['stratret'], data['pos'] = trade_logic(data, c)
        if logic=='youngbuck':
            data['stratret'], data['pos'] = trade_logic(data, c)
    return data#['stratret'], data['pos']

def sweetspotuser2(ticker, tickdict,logic, wf_window=50, lookback=1000, residvar_lookback=300, verbose=False):
    tickerdata = pd.read_pickle(''.join((datapath,ticker,'.pkl')))
    tickerdata['yesteresid'] = tickerdata['resid'].shift(1)
    tickerdata['residvar'] = [np.std(tickerdata.resid.iloc[i-residvar_lookback:i]) for i in range(len(tickerdata))]
    allrets=pd.Series()
    allpos=pd.Series()
    start = 0
    stop=lookback
    
    kill=False
    while kill==False:
        
        
        if stop>len(tickerdata):
            kill=True
            pass
        
        processes = 4
        sets = {}
        for i in range(processes):
            sets[i] = tickerdata[start:stop]
            start +=wf_window
            stop+=wf_window
            if stop>len(tickerdata):
                kill=True
                break
        '''if verbose:
            print('Step')
            print('All data')
            print(data.head(1).index)
            print(data.tail(1).index)'''
        
        
        #need  to fix these:
        p=Pool(processes)
        fourframes = [p.apply(get_sweetspot, args=(sets[x], logic, wf_window,)) for x in sets]
        p.close()
        p.join()    
        
        for i in range(len(fourframes)):
            allrets = pd.concat([allrets, fourframes[i]['stratret']])
            allpos = pd.concat([allpos, fourframes[i]['pos']])
            print(len(allrets))
    print(len(allrets))
    eqcurve = np.cumprod(3*allrets+1)
    return eqcurve[-2], allrets, allpos
    
    
    
    
            
            
    


def calc_symboldata(key, tickdict, logic, wf_window, lookback, residvar_lookback, verbose, numstrats):
    path = '_'.join(('/home/ubuntu/Notebooks/tradetest/testoutput2', logic, str(wf_window), str(lookback), str(residvar_lookback)))
    path2 = '_'.join(('/home/ubuntu/Notebooks/tradetest/testcurve2', logic, str(wf_window), str(lookback), str(residvar_lookback)))
    print(path)
    if os.path.exists(path):
        pass
    else:
        os.mkdir(path)
    
    if os.path.exists(path2):
        pass
    else:
        os.mkdir(path2)
    #path = '_'.join((path, logic, str(wf_window), str(lookback), str(residvar_lookback)))
    #path2 = '_'.join((path2, logic, str(wf_window), str(lookback), str(residvar_lookback)))
    print('')
    print(numstrats)
    numstrats+=1
    print('symbol: %s: ' % key)
    keypath = '/'.join((path,key))
    keypath2 = '/'.join((path2,key))
    if os.path.exists(keypath):
        print('found')
        return numstrats
    #r, e, p = sweetspotuser2(key, tickdict, logic, wf_window, lookback, residvar_lookback, verbose=verbose)
    
    try:
        r, e, p = sweetspotuser2(key, tickdict, logic, wf_window, lookback, residvar_lookback, verbose=verbose)
    except:
        print('FAILED')
        return numstrats
    
    
        
    a = [x for x in e if x!=0]
        
    indvspecs=pd.DataFrame()
    indvspecs['return'] =r
    indvspecs['vol'] = np.std(e)
    indvspecs['avol'] = np.std(a)
    indvspecs['sharpe'] = r/np.std(e)
    indvspecs['asharpe'] = r/np.std(a)
        
    indvspecs['rets'] = e
        #indvspecs['maxdd']
        #indvspecs['romad']
        #symbolspecs[key] = indvspecs
        
    indvspecs.to_pickle(keypath)
    e.to_pickle(keypath2)
    
    return numstrats

        

def main3(tickdict,logic='youngbuck',wf_window=50, lookback=1000, residvar_lookback=300,verbose=False, plot=True):
    def dd(pnl):
        max_accum = np.maximum.accumulate(pnl)
        max_curr_df = np.subtract(max_accum,pnl)
        #max_drawdown = np.amax(max_curr_df)
        return max(max_curr_df)
    
    portf = []
    porteq = pd.Series()
    numstrats = 0
    dds=[]
    symbolspecs={}
    
    
       
    it = iter(tickdict)
    
        
    #def f(key_):  
        #########THIS IS WHAT MAIN3 CALLS#########
     #   calc_symboldata(key_, tickdict, logic, wf_window, lookback, residvar_lookback, verbose, numstrats)
    '''for key_ in tickdict:
        f(key_)'''
    #for key in it:
    processes=1
    
    if processes==1:
        for key_ in tickdict:
            numstrats+=1
            calc_symboldata(key_, tickdict, logic, wf_window, lookback, residvar_lookback, verbose, numstrats)
    else:
        for j in zip(*[iter(tickdict)]*processes):

            #j=[key, next(it)]
            print(j)
            #numstrats = calc_symboldata(key, tickdict, logic, wf_window, lookback, residvar_lookback, verbose, numstrats)
            p=Pool(processes)
            [p.apply_async(calc_symboldata, args=(j[x], tickdict, logic, wf_window, lookback, residvar_lookback, verbose, numstrats,)) for x in range(processes)]
            p.close()
            p.join()    
        
        
    
    return #symbolspecs







if __name__ == '__main__':
    datapath = '../testlocation/'
    tickdict = get_symbols.main()
    #tickdict = get_tickdict(sdf, 5, gs=False, sample=False)
    
    
    symbolspecs_everything_y=main3(tickdict, logic='oldfart', wf_window=50, lookback=1000, residvar_lookback=200, verbose=False)
    '''
    symbolspecs_everything_y=main3(tickdict, logic='youngbuck', wf_window=50, lookback=1000, residvar_lookback=300, verbose=False)
    symbolspecs_everything_y=main3(tickdict, logic='oldfart', wf_window=50, lookback=1000, residvar_lookback=300, verbose=False)
    symbolspecs_everything_y=main3(tickdict, logic='oldfart', wf_window=50, lookback=1000, residvar_lookback=100, verbose=False)
    symbolspecs_everything_y=main3(tickdict, logic='youngbuck', wf_window=50, lookback=1000, residvar_lookback=100, verbose=False)
    '''
    
