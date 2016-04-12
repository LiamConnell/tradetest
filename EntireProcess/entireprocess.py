import sys
sys.path.append('../scrape_tickerdata_[p1]')
sys.path.append('../strategy_results_[p2]')
sys.path.append('../produce_report_[p3]')

import scrape_exec
import strat_exec
import pa_exec



#1 scrape_exec.main() 
get_data=False
price_datapath = '../data/pricedata/' 
tick_datapath='../data/tickdict/'
if get_data:
    scrape_exec.main(price_datapath, tick_datapath)
    
#2 strat_exec.main() 
tick_directory = tick_datapath
strat_out = '../data/youngbuck/'
logic = 'youngbuck'
#strat_exec.main(tick_directory, strat_out, logic, wf_window=50, lookback=1000, residvar_lookback=200)

#3 pa_exec.main() 
pa_path = strat_out
pa_exec.main(pa_path, N=100, metric='rets')

#seems like rets does best then sharpenz