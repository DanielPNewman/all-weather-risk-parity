import riskparityportfolio as rpp
import yaml
import pandas as pd
import numpy as np
import os

def get_weights_within_environment(daily_log_returns):
    """
    Inputs:
    - 'daily_log_returns' dataframe which was saved as  .csv was saved during
        get-ticker-time-series.py
    - global variables: 'environments', data_path' and 'portfolio_name'
        - 'environments' is a list of economic environments,
            e.g. ['RISING_GROWTH', 'RISING_INFLATION', etc.]
        - 'data_path' and 'portfolio_name' are both settings from config

    Outputs:
    - returns 'weights_within_environment' DataFrame
    - saves weights_within_environment dataframe as a .csv, containing the
        weights for each ticker WITHIN each environment
    """
    # create empty df
    df_merge = pd.DataFrame({'environment': [], 'ticker': [], 'weight': [],
                            'risk_contribution': []})
    for environment in environments:
        # creates a covariance matrix (numpy.ndarray) from time-series of assets
        cov = daily_log_returns[environments[environment]].cov().to_numpy()
        # create the desired risk budgeting vector (i.e. equal risk contributions)
        risk_budget = np.ones(len(cov)) / len(cov)
        # get the portfolio weights
        weights = rpp.vanilla.design(cov, risk_budget)
        # check risk contributions
        risk_contributions = \
        (weights @ (cov * weights)) / np.sum((weights @ (cov * weights)))
        if (not np.array_equal(risk_contributions.round(2), risk_budget.round(2))):
            raise Exception('Error! The risk contributions do not match risk budget')
        # make df
        df = pd.DataFrame({ 'environment': environment,
                            'ticker': list(environments[environment]),
                            'environment': environment,
                            'weight': list(weights),
                            'risk_contribution': list(risk_contributions)})
        df_merge = df_merge.append(df, sort=False)
        df_merge.to_csv(data_path+portfolio_name+'weights_within_environment.csv', \
                        index = False)
    return df_merge

def get_weights_between_environments(daily_log_returns, weights_within_environment):
    """
    Inputs:
    - 'daily_log_returns' dataframe which was saved as  .csv was saved during
        get-ticker-time-series.py
    - 'weights_within_environment' datafame returned by
        get_weights_within_environment()
    - also some global variables 'environments', 'data_path' and 'portfolio_name'

    Outputs:
    - returns 'weights_between_environments' DataFrame
    - saves 3 .csv files:
        - the weighted simple daily returns for each environment sub-portfoli
        - the weighted log daily returns for each environment sub-portfolio
        - weights for each environment, showing the contribution of each
            environment/sub-portfolio to the final all-weather portfolio
    """
    # need simple returns for combinding into weighted portfolios
    daily_simple_returns = daily_log_returns.apply(np.exp) - 1
    # create empty df
    df_merge = pd.DataFrame(index=daily_log_returns.index)
    for environment in environments:
        w = weights_within_environment['weight'].\
            loc[weights_within_environment['environment'] == environment]
        R = daily_simple_returns[environments[environment]]
        environment_simple_returns = R.to_numpy() @ w.to_numpy()
        df = pd.DataFrame({environment: environment_simple_returns}, index=daily_log_returns.index)
        df_merge = df_merge.join(df)
    df_merge.to_csv(data_path+portfolio_name+'weighted-simple-returns-per-environment.csv')
    # convert to log returns per environment:
    df_merge = df_merge + 1
    weighted_log_returns = df_merge.apply(np.log)
    weighted_log_returns.to_csv(data_path+portfolio_name
                                +'weighted-log-returns-per-environment.csv')
    # creates a covariance matrix (numpy.ndarray) from the 4 environment ime-series of weighted log returns
    cov = weighted_log_returns.cov().to_numpy()
    # create the desired risk budgeting vector (i.e. equal risk contributions)
    risk_budget = np.ones(len(cov)) / len(cov)
    # get the portfolio weights
    weights = rpp.vanilla.design(cov, risk_budget)
    # check risk contributions
    risk_contributions = (weights @ (cov * weights)) / np.sum((weights @ (cov * weights)))
    if (not np.array_equal(risk_contributions.round(2), risk_budget.round(2))):
        raise Exception('Error! The risk contributions are not in line with the risk budget')
    weights_between_environments = pd.DataFrame({'environment': list(environments.keys()),
                                                'weight': list(weights),
                                                'risk_contribution': list(risk_contributions)})
    weights_between_environments.to_csv(data_path+portfolio_name
                                        +'weights_between_environments.csv', index = False)
    return weights_between_environments

def get_final_ticker_weights(weights_within_environment, weights_between_environments):
    """
    Inputs:
    - 'weights_within_environment' DataFrame from
        get_weights_within_environment() function
    - 'weights_between_environments' DataFrame from
        get_weights_between_environments() function
    - global variables 'environments', 'data_path' and 'portfolio_name'
        - 'environments' is a list of economic environments,
            e.g. ['RISING_GROWTH', 'RISING_INFLATION', etc.]
        - 'data_path' and 'portfolio_name' are both settings from config

    Outputs:
    - Saves final_ticker_weights as a .csv, containing the final ticker
        weights for the all-weather portfolio
    """
    weights_within_environment = weights_within_environment.\
                                 rename(columns={"weight": "ticker_weight"})
    weights_within_environment = weights_within_environment.\
                                 set_index('environment').drop(['risk_contribution'], axis=1)
    weights_between_environments = weights_between_environments.\
                                 rename(columns={"weight": "environment_weight"})
    weights_between_environments = weights_between_environments.\
                                 set_index('environment').drop(['risk_contribution'], axis=1)
    df_merge = weights_within_environment.join(weights_between_environments)
    df_merge['weight'] = df_merge['ticker_weight']*df_merge['environment_weight']
    final_ticker_weights = df_merge[['ticker','weight']].groupby(['ticker']).sum()
    final_ticker_weights.to_csv(results_path+portfolio_name+'final-ticker-weights.csv')


def main():
    global environments, portfolio_name, data_path, results_path
    config = yaml.safe_load(open('portfolio-settings.yaml'))
    environments = config['ENVIRONMENTS']
    portfolio_name = config['PORTFOLIO_NAME']+'-'
    data_path = config['DATA_PATH']
    results_path = config['RESULTS_PATH']
    # The daily_log_returns .csv was saved during get-ticker-time-series.py
    daily_log_returns = pd.read_csv(data_path+portfolio_name
                                    +'daily-log-returns-per-ticker.csv', index_col = 0)
    # dn: uncomment below to restrict time, to test if weights remain stable.
    #daily_log_returns = daily_log_returns.loc[(daily_log_returns.index>='2012-03-14') & (daily_log_returns.index<='2019-07-19')]
    weights_within_environment = get_weights_within_environment(daily_log_returns)
    weights_between_environments = \
        get_weights_between_environments(daily_log_returns, weights_within_environment)
    get_final_ticker_weights(weights_within_environment, weights_between_environments)

if __name__ == '__main__':
    print("Starting " + os.path.realpath(__file__))
    main()
