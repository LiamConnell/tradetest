import sys
sys.path.append('../')
import get_symbols
import os
import pandas as pd
import numpy as np
from yahoo_finance import Share
import datetime
from datetime import datetime
from sklearn.linear_model import LinearRegression
import time
import smoothing_fns as smf

def get_dailyret(ser):
    return (ser.shift(-1) - ser)/ser

def call_filters(data):
    
    
    #data['gh_filter'] = smf.g_h_filter(np.array(data.Close), g = .5, h=.5)
    #data['unikal_prediction'], data['kal_smooth'] = smf.kalman_filter(np.array(data.Close), 1, .01)
    
    from filterpy.common import Q_discrete_white_noise
    Q = Q_discrete_white_noise(dim=2, dt=1., var=0.0035)
    
    xs , cov = smf.run(P=5, R=0, Q=Q, data=data)
    
    data['kal_mean'], data['kal_vel'], data['kal_pricecov'], data['kal_velcov'] = xs[:,0], xs[:,1], cov[:,0][:,0], cov[:,1][:,1]
    
    data['smooth'], data['trend'] = smf.get_smooth_val(data.Close, 50)
    data['resid'] = data.Close-data['smooth']
    #remember I also make this column here!
    data['dailyrets'] = get_dailyret(data.Close)
    
    return data
    
def get_ticker_data(strat, fin_data_path = '../data/pricedata'):
    ''' this should have parameters
        date range
        type of smooth val (which function)
    '''
    start = '2007-05-02'
    end = '2015-12-31'
    path = ''.join((fin_data_path, strat, '_', start, end))
    if os.path.exists(path):
        data = pd.read_pickle(path)
        print('found data')
    else:
        data = pd.DataFrame(Share(strat).get_historical(start, end))
        print('fetched data')
        data.Date = [datetime.strptime(data.Date.iloc[i], '%Y-%m-%d') for i in data.index]
        data.index = data.Date
        data = data.iloc[::-1]
        data.Close = [float(x) for x in data.Adj_Close]
        data.to_pickle(path)
    return data

    
    

def get_tickdict(tickers, price_datapath = '../data/pricedata/', tick_datapath='../data/tickdict/' ):
    
    numstrats = 0
    
    if not os.path.exists(price_datapath):
        os.makedirs(price_datapath)
    if not os.path.exists(tick_datapath):
        os.makedirs(tick_datapath)
    
    for ticker in tickers:
        print(numstrats)
        print(ticker)
        
        #saves df of price data from yahoo
        try:
            start = time.time()
            data = get_ticker_data(ticker, fin_data_path = price_datapath)
            end=time.time()
            print('fetch price data: %d' % int(end-start))
        except:
            continue
        
        #maybe add logic here for saving? depends on computing time
        try:
            start = time.time()
            data = call_filters(data)
            end=time.time()
            print('compute and save smoothing function: %d' % int(end-start))
        except:
            continue
        data.to_pickle(''.join((tick_datapath, ticker)))
        
        numstrats+=1 
        
        
    return 

