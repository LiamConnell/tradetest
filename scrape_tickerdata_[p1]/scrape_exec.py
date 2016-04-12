import scrape_fns as sf
import sys
import os
sys.path.append('../')
import get_symbols


#get tickers
tickers = get_symbols.main()
    
def main(price_datapath = '../data/pricedata/', tick_datapath='../data/tickdict2_24/'):
    #call function to get data and put it into a specific place
    sf.get_tickdict(tickers, price_datapath, tick_datapath)
    
if __name__ == '__main__':
    main()