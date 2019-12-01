import yaml
import pandas as pd
import numpy as np
from plotnine import *
from mizani.breaks import date_breaks
from mizani.formatters import date_format
from datetime import datetime
import warnings
import os

def get_daily_portfolio_returns(daily_log_returns, final_ticker_weights):
    """
    Inputs:
    - 'daily_log_returns' DataFrame with log returns series for each ticker
    - 'final_ticker_weights' DataFrame with each tickers weights

    Outputs:
    - 'portfolio_simple_returns' DataFrame
    - 'portfolio_cumulative_returns' DataFrame
    """
    # need ticker simple returns to combine as weighted portfolio simple returns
    daily_simple_returns = daily_log_returns.apply(np.exp) - 1
    R = daily_simple_returns
    w = final_ticker_weights['weight']
    # matrix multiplication to get weighted simple return for each day
    portfolio_simple_returns = R.to_numpy() @ w.to_numpy()
    portfolio_simple_returns = \
        pd.DataFrame({'portfolio_simple_returns': portfolio_simple_returns}, \
        index=daily_simple_returns.index)
    portfolio_cumulative_returns = portfolio_simple_returns.cumsum()
    portfolio_cumulative_returns = portfolio_cumulative_returns. \
                                rename(columns={"portfolio_simple_returns": "returns"})
    return portfolio_simple_returns, portfolio_cumulative_returns

def plot_portfolio_vs_benchmark(cumulative_returns, benchmark_cum_returns):
    benchmark_cum_returns = benchmark_cum_returns.rename(columns={"benchmark": "returns"})
    benchmark_cum_returns['key'] = "benchmark"
    cumulative_returns['key'] = "portfolio"
    cumulative_returns["returns"] = cumulative_returns["returns"]
    df = cumulative_returns.append(benchmark_cum_returns)
    df.index.name = 'date'
    df.reset_index(level=0, inplace=True)
    df['returns'] = df['returns']*100
    warnings.filterwarnings('ignore')
    df.to_csv(data_path+portfolio_name
                        +'returns.csv', header = True)
    r = (ggplot(df)
         + aes(x = 'date', y = 'returns', color='key', group='key')
         + geom_line()
         + scale_x_datetime(breaks=date_breaks('1 years'), labels=date_format('%Y'))
         + theme(axis_text_x=element_text(rotation=90, hjust=1))
         + labs(title=portfolio_name+'portfolio vs. benchmark',
                y = 'Returns %')
         )
    r.save(filename=portfolio_name+'returns.png', \
            format="png", path=results_path, width = 6.4, height = 4.8, dpi=125)
    warnings.filterwarnings('default')


def plot_drawdowns(cumulative_returns, benchmark_cum_returns):
    """Any time the cumulative returns dips below the current cumulative
    maximum returns, it's a drawdown. Drawdowns are measured as a percentage of
    that maximum cumulative return, in effect, measured from peak equity."""
    benchmark_drawdown = get_drawdown(benchmark_cum_returns)
    benchmark_drawdown = benchmark_drawdown.to_frame()
    benchmark_drawdown = benchmark_drawdown.rename(columns={"benchmark": "drawdown"})
    benchmark_drawdown['key'] = "benchmark"
    benchmark_drawdown.index.name = 'date'
    benchmark_drawdown.reset_index(level=0, inplace=True)
    portfolio_drawdown = get_drawdown(cumulative_returns)
    portfolio_drawdown = portfolio_drawdown.to_frame()
    portfolio_drawdown['key'] = "portfolio"
    portfolio_drawdown = portfolio_drawdown.rename(columns={"returns": "drawdown"})
    portfolio_drawdown.index.name = 'date'
    portfolio_drawdown.reset_index(level=0, inplace=True)
    mask = benchmark_drawdown.date.isin(portfolio_drawdown.date)
    benchmark_drawdown = benchmark_drawdown[mask]
    df = portfolio_drawdown.append(benchmark_drawdown)
    df.to_csv(data_path+portfolio_name
                        +'drawdowns.csv', header = True)
    warnings.filterwarnings('ignore')
    d = (ggplot(df)
         + aes(x = 'date', y = 'drawdown', color='key', group='key')
         + geom_line()
         + scale_x_datetime(breaks=date_breaks('1 years'), labels=date_format('%Y'))
         + theme(axis_text_x=element_text(rotation=90, hjust=1))
         + labs(title=portfolio_name+'portfolio vs. benchmark',
                y = 'Drawdown % (change peak to trough)')
         )
    d.save(filename=portfolio_name+'drawdowns.png', \
        format="png", path=results_path, width = 6.4, height = 4.8, dpi=125)
    warnings.filterwarnings('default')


def get_portfolio_stats(cumulative_returns, simple_returns, \
                        benchmark_cum_returns, benchmark_simple_returns):
    portfolio_max_drawdown = get_max_drawdown(cumulative_returns)/100
    benchmark_max_drawdown = get_max_drawdown(benchmark_cum_returns)/100
    max_drawdown = combine_into_df(portfolio_max_drawdown, benchmark_max_drawdown, "max_drawdown")
    portfolio_r_r_ratio = get_return_risk_ratio(simple_returns)
    benchmark_r_r_ratio = get_return_risk_ratio(benchmark_simple_returns)
    r_r_ratio = combine_into_df(portfolio_r_r_ratio, benchmark_r_r_ratio, "return_risk_ratio")
    portfolio_cagr = get_cagr(cumulative_returns)
    benchmark_cagr = get_cagr(benchmark_cum_returns)
    cagr = combine_into_df(portfolio_cagr, benchmark_cagr, "annual_return")
    portfolio_stats = cagr.join(max_drawdown).join(r_r_ratio)
    portfolio_stats.to_csv(results_path+portfolio_name
                        +'performance_stats.csv', header = True)

def combine_into_df(portfolio_stat, benchmark_stat, stat_name):
    df = (pd.Series(portfolio_stat).append(pd.Series(benchmark_stat))).to_frame()
    df = df.set_index(pd.Index(['portfolio', 'benchmark']))
    df = df.rename(columns={0: stat_name})
    return df

def get_cagr(cum_returns):
    cum_returns = cum_returns.iloc[:, 0] # change it to a Series
    date_format = "%Y-%m-%d"
    a = datetime.strptime(cum_returns.index[0], date_format)
    b = datetime.strptime(cum_returns.index[-1], date_format)
    num_years = float((b - a).days) / 365
    total_return = cum_returns.iloc[-1]
    annual_return = (1 + total_return)**(1/num_years) - 1
    return annual_return

def get_max_drawdown(cum_returns):
    cum_returns = cum_returns.iloc[:, 0] # change it to a Series:
    cum_returns = cum_returns+1
    max_return = cum_returns.cummax()
    drawdown = cum_returns.sub(max_return).div(max_return)*100
    return drawdown.min()

def get_drawdown(cum_returns):
    cum_returns = cum_returns.iloc[:, 0] # change it to a Series:
    cum_returns = cum_returns+1
    max_return = cum_returns.cummax()
    drawdown = cum_returns.sub(max_return).div(max_return)*100
    return drawdown

def get_return_risk_ratio(returns_non_cumulative):
    return np.mean(returns_non_cumulative) / np.std(returns_non_cumulative)

def main():
    global config, environments, portfolio_name, data_path, results_path
    config = yaml.safe_load(open('portfolio-settings.yaml'))
    environments = config['ENVIRONMENTS']
    portfolio_name = config['PORTFOLIO_NAME']+'-'
    data_path = config['DATA_PATH']
    results_path = config['RESULTS_PATH']
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    # The daily_log_returns .csv was saved during get-ticker-time-series.py
    daily_log_returns = pd.read_csv(data_path+portfolio_name
                                    +'daily-log-returns-per-ticker.csv', index_col = 0)
    benchmark_simple_returns = pd.read_csv(data_path+portfolio_name
                                        +'benchmark-simple-returns.csv', index_col = 0)
    benchmark_cum_returns = benchmark_simple_returns.cumsum()
    final_ticker_weights = pd.read_csv(results_path+portfolio_name
                                    +'final-ticker-weights.csv')
    simple_returns, cumulative_returns = \
        get_daily_portfolio_returns(daily_log_returns, final_ticker_weights)
    get_portfolio_stats(cumulative_returns, simple_returns, \
                        benchmark_cum_returns, benchmark_simple_returns)
    # plotnine has annoying warnings, couldn't figure out how to suppress
    plot_portfolio_vs_benchmark(cumulative_returns, benchmark_cum_returns)
    plot_drawdowns(cumulative_returns, benchmark_cum_returns)
    # save portfolio settings in results folder
    with open(results_path+config['PORTFOLIO_NAME']+'.yml', 'w') as outfile:
        yaml.dump(config, outfile)


if __name__ == '__main__':
    print("Starting " + os.path.realpath(__file__))
    main()
