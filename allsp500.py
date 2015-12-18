#import pyfolio as pf
import random
import pandas as pd
import numpy as np
from yahoo_finance import Share
import matplotlib
import datetime
from datetime import datetime
from sklearn.linear_model import LinearRegression


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



def get_stratret(row, threshold=11):
    if row['resid']>row['residvar']*threshold:
        return -row['dailyrets']
    elif row['resid']<-row['residvar']*threshold:
        return row['dailyrets']
    else:
        return 0
    
    
    
    
def get_dfs(strat):
    data = pd.DataFrame(Share(strat).get_historical('2010-05-02', '2014-12-12'))
    print('fetched data')
    data.Date = [datetime.strptime(data.Date.iloc[i], '%Y-%m-%d') for i in data.index]
    data.index = data.Date
    data = data.iloc[::-1]
    data.Close = [float(x) for x in data.Close]
    data['smooth'], data['trend'] = get_smooth_val(data.Close, 50)
    data['resid'] = data.Close-data['smooth']
    data['dailyrets'] = get_dailyret(data.Close)
    return data

def sweetspotuser(ticker, tickdict):
    cs=[]
    eqs=[]
    data = tickdict[ticker]
    data['residvar'] = [np.std(data.resid.iloc[i-100:i]) for i in range(len(data))]
    for x in range(200):
        c = .01*x
        #thresh = c*np.std(data['resid'])
        data['stratret'] = data.apply(get_stratret,args = (c,), axis = 1)
        eqcurve = np.cumprod(3*data.stratret+1)
        cs.append(c)
        eqs.append(eqcurve[-250])
    #plot(cs,eqs)
    #show()
    data  = tickdict[ticker].tail(250)
    if max(eqs)<1.1:
        print('nein!')
        return 
    c = cs[np.argmax(eqs)]
    data['stratret'] = data.apply(get_stratret,args = (c,), axis = 1)
    eqcurve = np.cumprod(3*data.stratret+1)
    return eqcurve[-2], data['stratret']





def main1():
    import get_symbols
    sdf = get_symbols.main()
    rs =[]
    for i in range(200):
        rs.append(sdf[int(random.random()*len(sdf))])
    sdf = rs
    tickdict = {}
    numstrats = 0
    for ticker in sdf:
        print(numstrats)
        print(ticker)
        try:
            tickdict[ticker] = get_dfs(ticker)
            #rets.append(main(ticker))
            numstrats+=1
            #print(rets[-1])
        except:
            print('failed')
            
    return sdf, tickdict

def main2(tickdict):
    def dd(pnl):
        max_accum = np.maximum.accumulate(pnl)
        max_curr_df = np.subtract(max_accum,pnl)
        #max_drawdown = np.amax(max_curr_df)
        return max(max_curr_df)
    portf = []
    porteq = pd.Series()
    numstrats = 0
    dds=[]
    for key in tickdict:
        print('')
        print(numstrats)
        numstrats+=1
        print('symbol: %s: ' % key)

        try:
            r, e = sweetspotuser(key, tickdict)
        except:
            continue
        print('return: %s' % r)
        portf.append(r)
        print('portfolio ret: %s' % np.mean(portf))

        if numstrats ==1:
            porteq = e
        else:
            porteq =((numstrats-1)* porteq+e)/numstrats
        print(np.prod(3*e+1))
        print(np.prod(3*porteq+1))
        portcurve = np.cumprod(3*porteq+1)
        print(portcurve[-2])
        dd1 = dd(np.cumprod(3*e+1))
        dds.append(dd1)
        pvol = np.std(3*porteq)*15.8745
        print(pvol)
        psharpe = int(portcurve[-2])-1/pvol
        print('port sharpe: %s' % psharpe)

        print('indv drawdown: %s' % dd1)
        print('portfolio dd: %s' % dd(portcurve))
        promad = portcurve[-2]-1/dd(portcurve)
        print('portf romad: %s' %promad)
        print('avg indv dd: %s' % np.mean(dds))
        print('avg inv ret: %s' % np.mean(portf))
        iromad = np.mean(portf)-1/np.mean(dds)
        print('avg indv romad: %s' %iromad)


if __name__ == "__main__":
    sdf, tickdict = main1()
    main2(tickdict)
