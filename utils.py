import numpy as np
import pandas as pd


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