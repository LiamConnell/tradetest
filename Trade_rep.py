import matplotlib
import seaborn

import random
import pandas as pd
import numpy as np
from yahoo_finance import Share
import matplotlib
import datetime
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib
import get_symbols

def get_dailyret(ser):
    return (ser.shift(-1) - ser)/ser


def get_smooth_val(ser, lookback):
    ###does not include today so that residual is relevant for return
    ls = []
    bs = []
    lr = LinearRegression()
    for i in range(len(ser)):
        a = ser[i-lookback:i].tolist()
        #print(a)
        if len(a) == 0:
            ls.append(np.nan)
            bs.append(np.nan)
        else:
            a = lr.fit(np.array(range(lookback)).reshape(lookback,1),np.array(a).reshape((lookback,1)))
            ls.append(float(a.predict(lookback)[0]))
            bs.append(float(a.coef_))
    return ls, bs
    
def get_dfs(strat):
    data = pd.DataFrame(Share(strat).get_historical('2007-05-02', '2015-12-31'))
    print('fetched data')
    data.Date = [datetime.strptime(data.Date.iloc[i], '%Y-%m-%d') for i in data.index]
    data.index = data.Date
    data = data.iloc[::-1]
    data.Close = [float(x) for x in data.Adj_Close]
    data['smooth'], data['trend'] = get_smooth_val(data.Close, 50)
    data['resid'] = data.Close-data['smooth']
    data['dailyrets'] = get_dailyret(data.Close)
    return data




def get_tickdict(sdf, num=4, gs=False, sample=True):
    numstrats = 0
    tickdict ={}
    if sample:
        sdf = random.sample(sdf,num)
    if gs:
        sdf = ['GS']
    for ticker in sdf:#['GS']:
        print(numstrats)
        print(ticker)
        try:
            tickdict[ticker] = get_dfs(ticker)
        except:
            continue
        numstrats+=1
    return  tickdict


sdf = get_symbols.main()
tickdict = get_tickdict(sdf, 5, gs=False)



def sweetspotuser2(ticker, tickdict,logic, wf_window=50, lookback=1000, residvar_lookback=300, verbose=False):
    allrets=pd.Series()
    allpos=pd.Series()
    start = 0
    stop=lookback
    while True:
        
        try:
            
            cs=[]
            eqs=[]
            if stop>len(tickdict[ticker]):
                break
            data = tickdict[ticker][start:stop]
            if verbose:
                print('Step')
                print('All data')
                print(data.head(1).index)
                print(data.tail(1).index)
            start +=wf_window
            stop+=wf_window
            data['yesteresid'] = data['resid'].shift(1)
            data['residvar'] = [np.std(data.resid.iloc[i-residvar_lookback:i]) for i in range(len(data))]
            for x in range(10):
                c = .15*x+1
                #thresh = c*np.std(data['resid'])
                if logic=='oldfart':
                    data['stratret'], pp = trade_logic(data, c)
                if logic=='youngbuck':
                    data['stratret'], pp = trade_logic2(data, c)
                
                eqcurve = np.cumprod(3*data.stratret+1)
                cs.append(c)
                eqs.append(eqcurve[-wf_window])#50])            #set to 250 for OOS
            #matplotlib.pyplot.plot(cs,eqs)
            #matplotlib.pyplot.show()
            #plot(cs,eqs)
            #show()
            data  = data.tail(wf_window)         #remove comment for OOS
            if verbose:
                print('added to final')
                print(data.head(1).index)
                print(data.tail(1).index)
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
            allrets = pd.concat([allrets, data['stratret']])
            allpos = pd.concat([allpos, data['pos']])
            #eqcurve = np.cumprod(3*data.stratret+1)
            #print(eqcurve.tail(1).index)
        except:
            break
    print(len(allrets))
    eqcurve = np.cumprod(3*allrets+1)
    return eqcurve[-2], allrets, allpos
    
            
            
    
def trade_logic(data, c):
    
    position = 'out'
    thresh = 0
    rets = []
    pos = []
    for i in range(data.shape[0]):
        threshold=data['residvar'].iloc[i]*c
        #threshold = 11
        if position == 'out':
            
            if data['resid'].iloc[i]>threshold:
                if data['resid'].iloc[i]<data['yesteresid'].iloc[i]:
                    position = 'short'
                    thresh = data['yesteresid'].iloc[i]
                    rets.append(-data['dailyrets'].iloc[i])
                    pos.append(-1)
                    continue
                else:
                    rets.append(0)
                    pos.append(0)
                    continue
                    
            if data['resid'].iloc[i]<-threshold:
                if data['resid'].iloc[i]>data['yesteresid'].iloc[i]:
                    position = 'long'
                    thresh = data['yesteresid'].iloc[i]
                    rets.append(data['dailyrets'].iloc[i])
                    pos.append(1)
                    continue
                else:
                    rets.append(0)
                    pos.append(0)
                    continue
            
            else:
                rets.append(0)
                pos.append(0)
                continue
               
        if position == 'long':
            if data['resid'].iloc[i]>0:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            if data['resid'].iloc[i]<thresh:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            else:
                rets.append(data['dailyrets'].iloc[i])
                pos.append(1)
                continue
        if position == 'short':
            if data['resid'].iloc[i]<0:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            if data['resid'].iloc[i]>thresh:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            else:
                rets.append(-data['dailyrets'].iloc[i])
                pos.append(-1)
                continue
    
    return pd.Series(rets, index = data.index), pd.Series(pos, index=data.index)


def trade_logic2(data, c):
    
    position = 'out'
    rets = []
    pos = []
    for i in range(data.shape[0]):
        threshold=data['residvar'].iloc[i]*c
        #threshold = 11
        if position == 'out':
            
            if data['resid'].iloc[i]>threshold:
                
                position = 'short'
                rets.append(-data['dailyrets'].iloc[i])
                pos.append(-1)
                continue
                
                    
            if data['resid'].iloc[i]<-threshold:
                
                position = 'long'
                rets.append(data['dailyrets'].iloc[i])
                pos.append(1)
                continue
                
            
            else:
                rets.append(0)
                pos.append(0)
                continue
               
        if position == 'long':
            if data['resid'].iloc[i]>-threshold:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            
            else:
                rets.append(data['dailyrets'].iloc[i])
                pos.append(1)
                continue
        if position == 'short':
            if data['resid'].iloc[i]<threshold:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            
            else:
                rets.append(-data['dailyrets'].iloc[i])
                pos.append(-1)
                continue
    
    return pd.Series(rets, index = data.index), pd.Series(pos, index=data.index)

def trade_logic2(data, c):
    
    position = 'out'
    rets = []
    pos = []
    for i in range(data.shape[0]):
        threshold=data['residvar'].iloc[i]*c
        #threshold = 11
        if position == 'out':
            
            if data['resid'].iloc[i]>threshold and data['trend'].iloc[i]<0:
                
                position = 'short'
                rets.append(-data['dailyrets'].iloc[i])
                pos.append(-1)
                continue
                
                    
            if data['resid'].iloc[i]<-threshold and data['trend'].iloc[i]>0:
                
                position = 'long'
                rets.append(data['dailyrets'].iloc[i])
                pos.append(1)
                continue
                
            
            else:
                rets.append(0)
                pos.append(0)
                continue
               
        if position == 'long':
            if data['resid'].iloc[i]>-threshold:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            
            else:
                rets.append(data['dailyrets'].iloc[i])
                pos.append(1)
                continue
        if position == 'short':
            if data['resid'].iloc[i]<threshold:
                position = 'out'
                rets.append(0)
                pos.append(0)
                continue
            
            else:
                rets.append(-data['dailyrets'].iloc[i])
                pos.append(-1)
                continue
    
    return pd.Series(rets, index = data.index), pd.Series(pos, index=data.index)


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
    for key in tickdict:
        print('')
        print(numstrats)
        
        print('symbol: %s: ' % key)

        #r, e,p = sweetspotuser2(key, tickdict)
        try:
            r, e, p = sweetspotuser2(key, tickdict,logic=logic, wf_window=50, lookback=1000, residvar_lookback=300, verbose=verbose)
        except:
            continue
            
        numstrats+=1
        
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
        symbolspecs[key] = indvspecs
            
        #print('return: %s' % r)
        portf.append(r)
        #print('portfolio ret: %s' % np.mean(portf)-1)

        if numstrats ==1:
            porteq = e
            portpos = abs(p)
            portexp = p
            porteq2 = e
            porteq3=e
        else:
            if len(e)!=len(porteq):
                continue
            porteq =((numstrats-1)* porteq+e)/numstrats
            portpos = portpos+abs(p)
            porteq2 = porteq2+e
            porteq3 = porteq2/portpos
            portexp = portexp+p
        #print('portfolio ret: %s' %np.prod(3*e+1))
        #print(np.prod(3*porteq+1))
        portcurve = np.cumprod(3*porteq+1)
        portcurve2 = np.cumprod(3*porteq3+1)
        print('portfolio ret: %s' % (portcurve[-2]-1))
        dd1 = dd(np.cumprod(3*e+1))
        dds.append(dd1)
        pvol = np.std(3*porteq)*15.8745
        print('portfolio vol: %s' %pvol)
        psharpe = (portcurve[-2]-1)/pvol
        print('port sharpe: %s' % psharpe)

        #print('indv drawdown: %s' % dd1)
        print('portfolio dd: %s' % dd(portcurve))
        promad = (portcurve[-2]-1)/dd(portcurve)
        print('portf romad: %s' %promad)
        #print('avg indv dd: %s' % np.mean(dds))
        #print('avg inv ret: %s' % np.mean(portf))
        iromad = np.mean(portf)-1/np.mean(dds)
        #print('avg indv romad: %s' %iromad)
        
        #if plot==True:
        matplotlib.pyplot.plot(e.index,np.cumprod(3*e+1))
        matplotlib.pyplot.show()
        matplotlib.pyplot.plot(portcurve.index,portcurve)
        matplotlib.pyplot.show()
        matplotlib.pyplot.plot(portcurve2.index,portcurve2)
        matplotlib.pyplot.show()
        matplotlib.pyplot.plot(portpos.index, portpos)
        matplotlib.pyplot.plot(portexp.index, portexp)
        matplotlib.pyplot.show()
        
    return symbolspecs



symbolspecs5=main3(tickdict, logic='youngbuck', wf_window=50, lookback=1000, residvar_lookback=100, verbose=False)