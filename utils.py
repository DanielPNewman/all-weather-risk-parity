import numpy as np
import pandas as pd
import riskparityportfolio as rpp


def read_and_validate_csv_time_series(path):
    df = pd.read_csv(path, index_col=0)
    if any(df.index.duplicated()):
        raise Exception(f'\nDirty Data!\n\n\
            There are duplicated dates or timestamps in\n\n\
            {path}\n\n\
            Each date or timestamp should only appear once in the timeseries\n')
    df.index = pd.to_datetime(df.index)  # change index to type datetime
    df = df.sort_index(ascending=True)  # sort starting with earliest date/timestamp
    return df


def calc_risk_parity_weights(cov):
    """
    Inputs:
    - 'cov': a covariance matrix (numpy.ndarray) from n log-returns time-series 

    Outputs:
    - 'weights': capital weight % needed, for each time-series from cov, to achieve the risk budget (i.e. risk parity)
    - 'risk_contributions': risk % contributed be each time-series from cov (contributions will be equal since budget is "risk-parity" here)
    """
    # create the desired risk budgeting vector (i.e. equal risk contributions)
    risk_budget = np.ones(len(cov)) / len(cov)
    # get the portfolio weights
    weights = rpp.vanilla.design(cov, risk_budget)
    # check risk contributions
    risk_contributions = (weights @ (cov * weights)) / np.sum((weights @ (cov * weights)))
    if (not np.array_equal(risk_contributions.round(2), risk_budget.round(2))):
        raise Exception('Error! The risk contributions do not match the risk budget')
    return weights, risk_contributions