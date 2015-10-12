import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy

#Here, we will conduct "event studies" to see how
#stock price "events" affect future prices. 
#We use the Event Profiler provided in QSTK.

def find_events(ls_symbols, d_data):
    #create an event matrix we start by reading the data for the specified 
    #time duration as mentioned in the tutorial 1. Then we calculate 
    #normalized returns for the equity data. 
    
    #c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    #remove NAN from price data
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
	
	#The event is defined as when the actual close
    #	of the stock price drops below $5.00
    df_close = d_data['actual_close']
		
    #Now we assess for each day whether an event occurred. We start by creating
    # a np.NAN matrix of similar size for marking the events. Then we fill in
    # each cell according to whether an event occurred on that date for 
    #that symbol
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    #for deepcopy see http://www.python-course.eu/deep_copy.php
	
	#timestamps for event range
    ldt_timestamps=df_close.index 
	
	#market price, which is indicated by 'SPY'
    ts_market = df_close['SPY']

    for s_sym in ls_symbols: # for each symbol
        for i in range(1, len(ldt_timestamps)): # for each day
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if price[t-1] >= 5.0 price[t] < 5.0 
            if f_symprice_yest >= 5.0 and f_symprice_today < 5.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
				
    return df_events

	
dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)
dt_timeofday = dt.timedelta(hours=16)
#dt_start=dt.datetime(2008, 1, 1)
#dt_end=dt.datetime(2009, 12, 31)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

#read list of stocks in S&P 500 in 2008 using the QSTK call 
dataobj = da.DataAccess('Yahoo')
ls_symbols = dataobj.get_symbols_from_list("sp5002012")
ls_symbols.append('SPY')
ls_keys = ['close', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)

d_data = dict(zip(ls_keys, ldf_data))
 
df_events = find_events(ls_symbols, d_data)
print "Creating Study"
ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='HW2_EventStudy_2012.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')