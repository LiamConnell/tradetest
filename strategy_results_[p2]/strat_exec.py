import trade_logic as tl
import random
import pandas as pd
import numpy as np
from yahoo_finance import Share
import datetime
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib
import sys
import os
from multiprocessing import Process, Pool

def break_data(data, wf_window, lookback):
    start = 0
    stop=lookback
    #while true:
        

def sweetspot(data, wf_window, lookback):
    start = 0
    end = lookback
    cols = [x for x in data.columns if 'stratret_' in x]

    #data['testret'] = 0
    tester = pd.Series()
    sels = pd.Series()
    posns = pd.Series()
    while True:
        slc = data.iloc[start:end]
        
        select = np.argmax(np.prod(slc[:-50][cols]+1))
        poselect = '_'.join(('pos', select.split(sep='_')[1]))
        
        sel = pd.Series(select, index = slc[-wf_window:].index)
        app = pd.Series(slc[-wf_window:][select])
        posn = pd.Series(slc[-wf_window:][poselect])
        
        tester = pd.concat([tester, app])
        posns = pd.concat([posns, posn])
        sels = pd.concat([sels, sel])

        start += wf_window
        end += wf_window
        

        if end > len(data):
            break


    data['stratret'] = tester
    data['param_select'] = sels
    data['pos'] = posns
    
    return data
    

def additional_formatting(data, residvar_lookback):
    data['yesteresid'] = data['resid'].shift(1)
    data['residvar'] = [np.std(data.resid.iloc[i-residvar_lookback:i]) for i in range(len(data))]
    return data

def main(tick_directory, out_dir, logic, wf_window, lookback, residvar_lookback):
    numstrats = 0
    print(numstrats)
    numstrats+=1
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    symbols = os.listdir(tick_directory)
    for symbol in symbols:
        print('symbol: %s: ' % symbol)
        
        #load and format data
        data= pd.read_pickle(''.join((tick_directory, symbol)))
        data = additional_formatting(data, residvar_lookback)
        
        
        for i in range(5):
            num = 1.5+(i/10)
            stratret = '_'.join(('stratret', str(num)))
            pos = '_'.join(('pos', str(num)))
            if logic=='youngbuck':
                data[stratret], data[pos] = tl.trade_logic2(data, num)
            if logic=='oldfart':
                data[stratret], data[pos] = tl.trade_logic(data, num)
        
        data = sweetspot(data, wf_window, lookback)
        #save data
        data.to_pickle(''.join((out_dir, symbol)))
                               
    
        
        
        

if __name__ == '__main__':
    tick_directory = '../data/tickdict/'
    out_dir = '../data/junkout/'
    logic = 'blag'
            
    
    main(tick_directory, out_dir, logic, wf_window=50, lookback=1000, residvar_lookback=200)