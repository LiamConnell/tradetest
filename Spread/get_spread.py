import pandas as pd
from yahoo_finance import Share
import datetime
from datetime import datetime
import numpy as np

def get_ticker_data(strat):
    start = '2007-05-02'
    end = '2015-12-31'

    data = pd.DataFrame(Share(strat).get_historical(start, end))
    print('fetched data')
    data.Date = [datetime.strptime(data.Date.iloc[i], '%Y-%m-%d') for i in data.index]
    data.index = data.Date
    data = data.iloc[::-1]
    data.Close = [float(x) for x in data.Adj_Close]
    return data

def get_dailyret(ser):
    return (ser.shift(-1) - ser)/ser

def get_spread(tsA, tsB, lookbackN=50, ts_type = None):
    if ts_type == 'names':
        tsA = get_ticker_data(tsA)
        tsB = get_ticker_data(tsB)
        ts_type = 'DF'
    if ts_type == 'DF':
        tsA = tsA.Close
        tsB = tsB.Close
        ts_type = 'close'
    if ts_type == 'close':
        tsA = get_dailyret(tsA)
        tsB = get_dailyret(tsB)
        ts_type = None
        
    
    hedge_std = pd.rolling_std(tsA, lookbackN)/pd.rolling_std(tsB,lookbackN)
    dailyretsofspread = tsA - tsB * hedge_std
    return dailyretsofspread