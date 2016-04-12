import pandas as pd
import numpy as np



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