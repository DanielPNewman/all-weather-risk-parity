from alpha_vantage.timeseries import TimeSeries
from datetime import datetime, timedelta
import yaml
import pandas as pd
import numpy as np
import os
import time
import sys
import yfinance as yf
from utils import (read_and_validate_csv_time_series)

def download_daily_adjusted_price(tickers, ts, data_path, custom_data_list):
    """
    Inputs:
    - List of stock tickers
    Outputs:
    - Each ticker's daily adjusted close price time series saved in a seperate .csv.
    - Returns the maximum start date out of all the ticker time series in the list.
    """
    first_date_list = []
    counter = 0
    for ticker in tickers:
        if ticker not in custom_data_list:
            counter += 1 #alpha_vantage only allows 5 ticker downloads per min so...
            if counter % 5==0: # pause script for 1 min every 5 downloads:
                time.sleep(60)
            try:
                ticker_data, _ = \
                    ts.get_daily_adjusted(symbol=ticker, outputsize='full')
                ticker_data = \
                    ticker_data.rename(columns={"5. adjusted close": "adjusted_close"})
            except Exception as e:
                print(str(e) + "...a problem calling the alpha_vantage API.\
                                trying the yfinance API instead...\n")
                handle = yf.Ticker(ticker)
                ticker_data = handle.history(period="max")
                ticker_data = ticker_data.reset_index()
                ticker_data = \
                    ticker_data.rename(columns={"Close": "adjusted_close", "Date": "date"})
                ticker_data = ticker_data.set_index('date')
            except Exception as e2:
                print(str(e2) + "\nBoth ticker data APIs failed")
                sys.exit(1) #quit this script
            adjusted_close = \
                ticker_data['adjusted_close'].loc[ticker_data['adjusted_close'] > 0]
            adjusted_close = adjusted_close.sort_index()
            adjusted_close.to_csv(data_path+ticker+'.csv', header = True)
            first_date = adjusted_close.index.min()
            first_date_list.append(first_date)
        max_first_date = pd.Series(first_date_list).max()
    return max_first_date.strftime('%Y-%m-%d')

def get_log_returns_series(tickers, max_first_date, data_path, portfolio_name):
    """
    Inputs:
    - List containing stock tickers
        representing the .csv files downloaded and saved by
        download_daily_adjusted_price().
    - Maximum start date out of all the time series in the list

    Outputs:
    -  Saves one .csv dataframe containing the the daily log returns of each
        ticker, date rows with missing data are removed.
    """
    #set max date to yesterday
    max_last_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    df_merge = pd.DataFrame(index=(pd.date_range(start=max_first_date, end=max_last_date)))
    for ticker in tickers:
        price_df = read_and_validate_csv_time_series(data_path+ticker+'.csv')
        price_df['log_return'] = np.log(price_df.adjusted_close
                                        / price_df.adjusted_close.shift(1))
        price_df = price_df.loc[(price_df.index>=max_first_date) & (price_df.index<=max_last_date)]
        log_returns = price_df['log_return']
        df = log_returns.to_frame().rename(columns={"log_return": ticker})
        df_merge = df_merge.join(df)
    df_merge = df_merge.dropna()
    df_merge.to_csv(data_path+portfolio_name
                    +'daily-log-returns-per-ticker.csv', header = True)

def get_benchmark_daily_returns(benchmark_tickers, benchmark_ticker_weights, \
                                ts, max_first_date, data_path, portfolio_name):
    max_last_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    df_merge = pd.DataFrame(index=(pd.date_range(start=max_first_date, end=max_last_date)))
    counter = 0
    for ticker in benchmark_tickers:
        counter += 1 #alpha_vantage only allows 5 ticker downloads per min so...
        if counter % 5==0: # pause script for 1 min every 5 downloads:
            time.sleep(60)
        ticker_data, _ = \
            ts.get_daily_adjusted(symbol=ticker, outputsize='full')
        ticker_data = \
            ticker_data.rename(columns={"5. adjusted close": "adjusted_close"})
        adjusted_close = \
            ticker_data['adjusted_close'].loc[ticker_data['adjusted_close'] > 0]
        adjusted_close = adjusted_close.loc[(adjusted_close.index>=max_first_date) & (adjusted_close.index<=max_last_date)]
        adjusted_close = adjusted_close.to_frame()
        adjusted_close = adjusted_close.sort_index()
        adjusted_close['simple_returns'] = ((adjusted_close.adjusted_close
                                            / adjusted_close.adjusted_close.shift(1))
                                            - 1)
        df = adjusted_close[['simple_returns']]
        df = df.rename(columns={"simple_returns": ticker})
        df_merge = df_merge.join(df)
    daily_simple_returns = df_merge.dropna()
    daily_simple_returns = daily_simple_returns.sort_index()
    R = daily_simple_returns.to_numpy()
    w = benchmark_ticker_weights
    benchmark_simple_returns = R @ w
    benchmark_simple_returns = benchmark_simple_returns
    benchmark_simple_returns = pd.DataFrame({'benchmark': benchmark_simple_returns}, \
                                             index=daily_simple_returns.index)
    benchmark_simple_returns = benchmark_simple_returns.sort_index()
    benchmark_simple_returns.to_csv(data_path+portfolio_name
                                    +'benchmark-simple-returns.csv', header = True)


def main():
    config = yaml.safe_load(open('portfolio-settings.yaml'))
    portfolio_name = config['PORTFOLIO_NAME']+'-'
    if portfolio_name != "INDEX-backtest-":
        tickers = {ticker for tickers in config['ENVIRONMENTS'].values() for ticker in tickers}
        data_path = config['DATA_PATH']
        custom_data_list = config['CUSTOM_DATA_LIST']
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        ts = TimeSeries(key=os.getenv("ALPHAVANTAGE_KEY"), output_format='pandas')
        max_first_date = download_daily_adjusted_price(tickers, ts, data_path, custom_data_list)
        get_log_returns_series(tickers, max_first_date, data_path, portfolio_name)
        benchmark_tickers = config['BENCHMARK_TICKERS']
        benchmark_ticker_weights = config['BENCHMARK_TICKER_WEIGHTS']
        time.sleep(60) ##alpha_vantage only allows 5 ticker downloads per min
        get_benchmark_daily_returns(benchmark_tickers, benchmark_ticker_weights, \
                                    ts, max_first_date, data_path, portfolio_name)

if __name__ == '__main__':
    print(f"Starting {os.path.realpath(__file__)}, this may take a while")
    main()
