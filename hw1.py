import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#QSTK supports portfolio construction and management, details at:
#http://wiki.quantsoftware.org/index.php?title=QuantSoftware_ToolKit

#this program simulates how the stocks in a given portfolio perform over time
#and computes the statistics of the final values of the stocks
#to see how much profit/loss you got with this portfolio

#function for iterating through a range of floats
#if x=0, y=1, then iterates through 0, .1, .2, .., .9, 1
#for portfolio optimizer to test every "legal" set of allocations to the
# 4 stocks. Keep track of the "best" portfolio


def simulate(dt_start, dt_end, ls_symbols, ls_allocations, benchmark_symbol):
    #ls_symbols contains list of equities/stocks that we're interested in. 
	#Ex: AAPL, GOOG (Apple, Google)
	#dt_start is start date, dt_end is end date (Ex: Jan 1st, 2014 to Dec 31st 2014)
	#ldt_timestamps is the list of timestamps that represent NYSE closing times between 
	#the start and end dates. 
	#We specify 16:00 hours because we want the data that was available to us 
	#at the close of the day. 
	#full explanation at: http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_1
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
	
	#We read data from Yahoo data source
	#ls_keys are the data types we want
	#ldf_data is a LIST of DATAFRAME objects which contain ls_keys
	#We then convert the ldf_data LIST into the  dictionary d_data
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values

	#benchmark values	
    ldf_data_benchmark = c_dataobj.get_data(ldt_timestamps, benchmark_symbol, ls_keys)
    d_data_benchmark = dict(zip(ls_keys, ldf_data_benchmark))
    na_price_benchmark = d_data_benchmark['close'].values
	
	#It can be difficult to see how the price of each stock varies over time 
	#when looking at a plot if one stock has a much higher/lower price than
	#the others and dominates
	#looking at the normalized prices it is easier to see the prices vs time
	#this normalizes the prices with respect to the first day's price
    #for each stock
    na_normalized_price = na_price / na_price[0, :]
    na_normalized_price_benchmark = na_price_benchmark / na_price_benchmark[0, :]
    

    #if ls_symbols=['AAPL', 'GLD', 'GOOG', 'XOM' then
    #na_price[0:50,3]) price for GOOG for 50 days
    #na_price[0:50,4]) price for XOM for 50 days

    #ls_allocations is input parameter
    # Allocations to the equities at the beginning of the simulation (e.g., 0.2, 0.3, 0.4, 0.1)

    #row-wise multiplication by weights
    na_weighted_price = na_normalized_price * ls_allocations
	#na_normalized_price[rows are days, columns are stocks]
	#ex: na_normalized_price[13,1] is normalized price on 14th day for 'GLD'
	
    #row-wise sum
    total_weightprice_perday = na_weighted_price.copy().sum(axis=1);
    #total_weightprice_perday is a Nx1 vector, where N is #of days (say, 50)
	#because it takes the sum of every stock per day
	#ex: na_weighted_price=[ ['AAPL', 'GLD', 'GOOG', 'XOM'],
	#					(1st day) [.35, .3, .5, .2],
	#						  ...,
	#					(last day)	  [.5,.3,.6,.7] ]
	#  total_weightprice_perday = [1.35 (1st day),
	#								...,
	#					(last day)	2.1]
	
	#np.sum([[2, 3], [4, 5]], axis=1) gives array([5,9])
	#np.sum([[2, 3], [4, 5]], axis=0) gives array([6,8])
	
	#Calculate returns for each day for each stock in the portfolio
	#the QSTK function returnize0 calculates this for us
    rets_weightprice_perday = total_weightprice_perday.copy()
    tsu.returnize0(rets_weightprice_perday)

    daily_ret = np.average(rets_weightprice_perday)
    #daily_ret = np.average(na_weighted_rets)
	
	#get standard dev of weighted returns
    vol = np.std(rets_weightprice_perday)
    #vol = np.std(na_weighted_rets)   

    #Sharpe ratio = (Mean portfolio return - Risk-free rate)/Standard deviation of portfolio return
    #problem states "Always assume you have 252 trading days in an year. And risk free rate = 0"
    sharpe = np.sqrt(252) * daily_ret / vol

	#cumulative return of total portfolio
    cum_ret = np.dot(na_price[-1]/na_price[0], np.transpose(ls_allocations))
    #negative index for array accesses elements starting with last index
    # ex) a= [1, 2, 3]
    #>>> print a[-2]
    #2
    #>>> print a[-1]
    #3
    #earlier, we had na_normalized_price = na_price / na_price[0, :]

    #print na_price[0, :]
    #[   74.43    53.12   435.23  1268.8     50.47]
    #print na_price[0]
    #[   74.43    53.12   435.23  1268.8     50.47]
    #print na_price[-1]
    #[  322.28   137.03   598.86  1257.88    70.33]

    return vol, daily_ret, sharpe, cum_ret, total_weightprice_perday, na_normalized_price_benchmark

	
	
	
	
startdate = dt.datetime(2011, 1, 1)
enddate = dt.datetime(2011, 12, 31)
dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)
al_symbols=['AAPL', 'GLD', 'GOOG', 'XOM']

#iterate through every legal set of allocations to find best portfolio
#which contains Highest Sharpe Ratio
#for v in float_iterator(v, 1.0, step):
sharpe_best= -1000000.0
vol_best=0.0
daily_ret_best=-1000000
cum_ret_best=0.0
total_weightprice_perday_best=0.0
na_normalized_price_benchmark_best = 0.0
v_opt=0.0
w_opt=0.0
x_opt=0.0
y_opt=0.0

for v in range(0,11,1):
    v_remain = 11 - v
    for w in range(0,v_remain,1):
        w_remain = 11-v-w
        for x in range(0, w_remain,1):
            y=10-v-w-x
            va=v*.1
            wa=w*.1
            xa=x*.1
            ya=y*.1
            vol, daily_ret, sharpe, cum_ret, total_weightprice_perday, na_normalized_price_benchmark = simulate(startdate, enddate, al_symbols, [va,wa,xa,ya], ['$SPX'])
            if (sharpe>sharpe_best):
                sharpe_best=sharpe
                vol_best=vol
                daily_ret_best=daily_ret
                cum_ret_best=cum_ret
                total_weightprice_perday_best=total_weightprice_perday
                na_normalized_price_benchmark_best = na_normalized_price_benchmark
                v_opt=va
                w_opt=wa
                x_opt=xa
                y_opt=ya
			   

#vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, ['AAPL', 'GLD', 'GOOG', 'XOM'], [0.4, 0.4, 0.0, 0.2])
print "Start Date :", startdate
print "End Date:",enddate
print "Symbols: ", '[%s]' % ', '.join(map(str, al_symbols))
#Map calls str for each element of al_symbols, creating a new list of strings
# that is then joined into one string with str.join. 
#Then, the % string formatting operator substitutes the string in
print "Optimal Allocation: [", v_opt, ", ",w_opt, ", ",x_opt, ", ", y_opt,"]"
print "Sharpe Ratio:", sharpe_best
print "Volatility (stdev of daily returns): ", vol_best
print "Average Daily Return:", daily_ret_best
print "Cumulative Return:", cum_ret_best

plt.clf()
plt.plot(ldt_timestamps, total_weightprice_perday_best)
plt.plot(ldt_timestamps, na_normalized_price_benchmark_best*total_weightprice_perday_best[0])
plt.legend(['Portfolio', 'Benchmark'], loc='best')
plt.ylabel('Fund Value', size='x-small')
plt.xlabel('Date', size='x-small')
locs, labels = plt.xticks(size='x-small')
plt.yticks(size='x-small')
plt.setp(labels,rotation=15)
plt.savefig('HW1_PortfolioValues.pdf', format='pdf')

startdate = dt.datetime(2010, 1, 1)
enddate = dt.datetime(2010, 12, 31)
vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, ['AXP', 'HPQ', 'IBM', 'HNZ'], [0.0, 0.0, 0.0, 1.0])
print "Sharpe Ratio:", sharpe
print "Volatility (stdev of daily returns): ", vol
print "Average Daily Return:", daily_ret
print "Cumulative Return:", cum_ret