import pandas as pd
import numpy as np
import os
import sys

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))


def performance_summary(ts):
    tsnz = np.array([x for x in ts if x!=0])
    years = (ts.index[-1]-ts.index[0]).days/365
    yearsnz = len(tsnz)/252
    
    
    ret = np.prod(ts+1)
    annret = ret**(1/years)
    annretnz = ret**(1/yearsnz)
    stdz = np.std(ts)*(252**.5)
    std = np.std(tsnz)*(252**.5)
    sharpez = (annret-1)/stdz
    sharpe = (annret-1)/std
    sharpenz = (annretnz-1)/std
    
    out = [ret-1, annret-1,annretnz-1, stdz, std, sharpez, sharpe,sharpenz]
    out = [truncate(x, 3) for x in out]
    return out
    

def get_summaries(dir_, mark=None, time=None, topn=None):
    if topn==None:
        symbols = os.listdir(dir_)
    else:
        symbols=topn
        
    out = {}
    for symbol in symbols:
        ts = pd.read_pickle(''.join((dir_, symbol)))['stratret']
        if len(ts) != 2184:
            continue
        ts = ts.dropna()
        try:
            if mark=='before':
                ts = ts[:time]
            if mark=='after':
                ts=ts[time:]
            if mark=='in':
                ts=ts[time]
            ret = performance_summary(ts)
            out[symbol] = ret
        except:
            continue
    df = pd.DataFrame.from_dict(out, orient='index')

    df.columns = ['rets', 'annret','annrtnz', 'stdz', 'std', 'sharpez', 'sharpe', 'sharpenz']
    return df

def top_N(summs, N, metric='rets'):
    return pd.DataFrame(summs.loc[x] for x in list(pd.Series(summs[metric], dtype='float64').dropna().nlargest(N).index))

def get_portfolio_ts(dir_,mark=None, time=None, topn=None):
    if topn==None:
        symbols = os.listdir(dir_)
    else:
        symbols=topn
        
    
    out = pd.DataFrame()
    for symbol in symbols:
        ts = pd.read_pickle(''.join((dir_, symbol)))['stratret']
        if mark=='before':
            ts = ts[:time]
        if mark=='after':
            ts=ts[time:]
        if mark=='in':
            ts=ts[time]
        if len(ts) >6:
            try:
                out[symbol]=ts
            except:
                print('symfail')
    return out.sum(axis=1)/out.shape[1]

def write_results(res, writepath):
    f=open(writepath, 'w')
    titles= ['rets', 'annret','annrtnz', 'stdz', 'stdev', 'sharpez', 'sharpe', 'sharpenz']
    f.write('\t'.join(([str(x) for x in titles])))
    f.write('\n')
    f.write('\t'.join(([str(x) for x in res])))
    f.close()

    
def get_wf_portfolio(dir_):
    symbols = os.listdir(dir_)
    start = 0
    end = 40
    step = 20
    allsers = pd.Series()
    allposs = pd.Series()
    while true:
        sers = pd.DataFrame()
        poss = pd.DataFrame()
        for symbol in symbols:
            ts = pd.read_pickle(''.join((dir_, symbol)))['2011 02':]['stratret']
            if len(ts) != 2184:
                continue
            ts = ts[start:end]
            pos = pd.read_pickle(''.join((dir_, symbol)))['2011 02':]['pos'][start:end]
            ts = ts.dropna()
            sers[symbol] = ts
            poss[symbol] = abs(pos)
        topn = list((sers+1).prod().sort_values(ascending=False)[:50].index)
        addser = sers[topn].sum(axis = 1)
        addpos = poss[topn].sum(axis = 1)
        allsers = pd.concat([allsers,addser])
        allposs = pd.concat([allposs, addpos])
        start +=step
        end+=step
        if end>1238:
            break
    return allsers, allposs


def main3(dir_, N, metric):
    outdir = '../data/performance_results/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    outdir_ = ''.join(('../data/performance_results/', dir_.split('../data/')[1]))
    if not os.path.exists(outdir_):
        os.makedirs(outdir_)
    
    #all
    summs = get_summaries(dir_, mark='after', time='2011')
    summs.to_csv(''.join((outdir_, 'all_individual.csv')), sep='\t')
    portf_ts = get_portfolio_ts(dir_, mark='after',time='2011')
    res = performance_summary(portf_ts)
    write_results(res, ''.join((outdir_, 'all_portf.txt')))
    
    #train
    summs = get_summaries(dir_, mark='before', time='2014')
    topn = top_N(summs, N, metric)
    summs = get_summaries(dir_, mark='before',time='2014', topn=list(topn.index))
    summs.to_csv(''.join((outdir_, 'train_individual.csv')), sep='\t')
    portf_ts = get_portfolio_ts(dir_, mark='before',time='2014', topn=list(topn.index))
    res = performance_summary(portf_ts)
    write_results(res, ''.join((outdir_, 'train_portf.txt')))
    
    #test
    summs = get_summaries(dir_, mark='after',time='2015', topn=list(topn.index))
    summs.to_csv(''.join((outdir_, 'test_individual.csv')), sep='\t')
    portf_ts = get_portfolio_ts(dir_, mark='after',time='2015', topn=list(topn.index))
    res = performance_summary(portf_ts)
    write_results(res, ''.join((outdir_, 'test_portf.txt')))
    
    #control
    summs = get_summaries(dir_, mark='after', time='2015')
    summs.to_csv(''.join((outdir_, 'control_individual.csv')), sep='\t')
    portf_ts = get_portfolio_ts(dir_, mark='after',time='2015')
    res = performance_summary(portf_ts)
    write_results(res, ''.join((outdir_, 'control_portf.txt')))
    
    #control(top)
    topn = top_N(summs, N, metric)
    summs = get_summaries(dir_, mark='after',time='2015', topn=list(topn.index))
    summs.to_csv(''.join((outdir_, 'control(top)_individual.csv')), sep='\t')
    portf_ts = get_portfolio_ts(dir_, mark='after',time='2015', topn=list(topn.index))
    res = performance_summary(portf_ts)
    write_results(res, ''.join((outdir_, 'control(top)_portf.txt')))
    

if __name__=='__main__':
    print(np.prod(get_portfolio_ts(sys.argv[1])+1))
