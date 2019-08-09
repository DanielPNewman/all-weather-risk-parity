# create all-weather risk parity weights and back-test

WORK IN PROGRESS! - _I plan to make a docker container for this eventually, but until then, follow the steps below:_

## requirements 
**python3.7 package requirements:**

- riskparityportfolio==0.0.7
- alpha_vantage
- yaml
- pandas 
- numpy
- plotnine
- mizani

_code in this repo currently uses an old package `riskparityportfolio 0.0.7`, so make sure you `pip install 'riskparityportfolio==0.0.7'` until I get time to fix this. I need to update the code to run with current version `riskparityportfolio 0.0.8` which had breaking changes_

## How to use:

1. install the python3.7 requirements listed above
2. Set up git lfs `git lfs install` then `git lfs track '*.csv'`
3. get a free `alphavantage` API key [here][1] and set the key as environment variable: ALPHAVANTAGE_KEY
4. Set your desired portfolio and benchmark tickers in `portfolio-settings.yaml`
5. Run `./build-and-backtest-portfolio.sh` which executes the following scripts:
	- get-ticker-time-series.py
	- calculate-all-weather-ticker-weights.py
	- assess-portfolio-historic-performance.py

6. See your results, they will be written to a `/results` subdirectory, along with a copy of the `portfolio-settings` related to each set of results.  



[1]: https://www.alphavantage.co/support/#api-key
