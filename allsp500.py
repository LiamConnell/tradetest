#import pyfolio as pf
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
    data = pd.DataFrame(Share(strat).get_historical('2010-05-02', '2015-12-12'))
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
    c = cs[np.argmax(eqs)]
    data['stratret'] = data.apply(get_stratret,args = (c,), axis = 1)
    eqcurve = np.cumprod(3*data.stratret+1)
    return eqcurve[-2], data['stratret']





def main():
    import get_symbols
    sdf = get_symbols.main()
    sdf = sdf[:2]
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
            
    portf = []
    porteq = pd.Series()
    numstrats = 0
    def dd(pnl):
        max_accum = np.maximum.accumulate(pnl)
        max_curr_df = np.subtract(max_accum,pnl)
        #max_drawdown = np.amax(max_curr_df)
        return max(max_curr_df)


    for key in tickdict:
        print('')
        print(numstrats)
        numstrats+=1
        print('symbol: %s: ' % key)

        try:
            r, e = sweetspotuser(key, tickdict)
        except:
            pass
        print('return: %s' % r)
        portf.append(r)
        print('portfolio ret: %s' % np.mean(portf))

        if numstrats ==1:
            porteq = e
        else:
            porteq = porteq+e
        print(porteq.head())
        print(e.head())
        print(np.prod(3*e+1))
        print(np.prod(3*porteq+1))
        portcurve = np.cumprod(3*porteq+1)
        print(portcurve[-2])
        print('drawdown: %s' % dd(np.cumprod(3*e+1)))
        print('portfolio dd: %s' % dd(portcurve))
        



if __name__ == "__main__":
    main()
