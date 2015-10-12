import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import csv


class Orders():
    def __init__(self, date, symbol, buysell, number):        
        self.date = date
		self.symbol = symbol
		self.buysell = buysell
        self.n_shares = number
		
		

dates = []
symbols = []
order_list=[]

starting_cash = float(sys.argv[1])
order_file = sys.argv[2]
out_file = sys.argv[3]

reader = csv.reader(open(order_file, 'rU'), delimiter=',')
for row in reader:
    print row
	#ex: 2008, 12, 3, AAPL, BUY, 130
	dates.append(dt.datetime(row[0],row[1],row[2]))
	symbols.append(row[3])
	each_order = Orders('date'=dates,row[3], row[4],row[5])
	order_list.append(each_order)

order_list.sort(['date'])

#remove duplicates
#set(listWithDuplicates) is an unordered collection without duplicates
#so it removes the duplicates in listWithDuplicates
uniqueDates = list(set(dates))
uniqueSymbols = list(set(symbols))
sortedDates=sorted(uniqueDates)
dt_start = sortedDates[0]
dt_end = sortedDates[-1] + dt.timedelta(days=1)

dataobj = da.DataAccess('Yahoo')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

#step 3: create dataframe that contains trade matrix
df_trade = np.zeros((len(ldt_timestamps), len(uniqueSymbols)))
df_trade = pd.DataFrame(df_trade, index=ldt_timestamps, columns=uniqueSymbols)

#step4: create timeseries containing cash values, all values are 0 initially
ts_cash = pd.TimeSeries(0.0, index=ldt_timestamps)
ts_cash = starting_cash

#iterate orders file and fill the number of shares for that 
#symbol and date to create trade matrix
reader = csv.reader(open(order_file, 'rU'), delimiter=',')
for orderrow in order_list:
    for index, row in df_trade.iterrows():
        if orderrow[3]=="BUY":
		   df_trade.set_value(index, orderrow[4], orderrow[5])
		   #df.set_value(index,column,new_value)
		   ts_cash[index] = ts_cash[index] - orderrow[5]
		elif orderrow[3]=="SELL":
		   df_trade.set_value(index, orderrow[4], -orderrow[5])
		   #df.set_value(index,column,new_value)
		   ts_cash[index] = ts_cash[index] + orderrow[5]  
		   
#step5: 
#append '_CASH' into the price date
df_close = d_data['close']
df_close['_CASH']=1.0
#if ls_symbols=['AAPL', 'GLD', 'GOOG', 'XOM' then
#df_close[0:50,3]) price for GOOG for 50 days
#df_close[0:50,4]) price for XOM for 50 days
#see hw1.py
	
	
#append cash time series into the trade matrix
df_trade['_CASH'] = ts_cash

#convert to holding matrix
#df_trade = df_trade.cumsum(axis=1)
#axis=1 means sum over columns
#see http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.cumsum.html

#dot product on price (df_close) and holding/trade matrix (df_trade) to 
#calculate portfolio on each date

for index, row in df_trade.iterrows():
        portfolio_value = np.dot(row.values, df_close[index].values)
        ts_fund[index] = portfolio_value
		
#write this to csv
writer = csv.writer(open(out_file, 'rU'), delimiter=',')
for row_index in ts_fund.index:
	row_to_enter = [row_index.year, row_index.month,
                        row_index.day, ts_fund[row_index]]
    writer.writerow(row_to_enter)