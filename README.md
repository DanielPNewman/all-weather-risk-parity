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

_code in this repo currently runs with an old package `riskparityportfolio 0.0.7`, so make sure you `pip install 'riskparityportfolio==0.0.7'` until I get time to fix this. I need to update the code to run with current version `riskparityportfolio 0.0.8` which I think had breaking changes_

## How to use:

1. install the python3.7 requirements listed above
2. Set up git lfs `git lfs install` then `git lfs track '*.csv'`
3. get a free `alphavantage` API key [here][1] and set the key as environment variable: ALPHAVANTAGE_KEY
4. Set your desired portfolio and benchmark tickers in `portfolio-settings.yaml`. Make sure the tickers you use have enough historical data (e.g. at least 7 years) available for volatility estimates. 
5. Run `./build-and-backtest-portfolio.sh` which executes the following scripts:
	- get-ticker-time-series.py
	- calculate-all-weather-ticker-weights.py
	- assess-portfolio-historic-performance.py

6. See your results, they will be written to a `/results` subdirectory, along with a copy of the `portfolio-settings` related to each set of results.  

## WTF is an "All-Weather" portfolio anyway?

```
“If you can’t predict the future with much certainty and you don’t know 
which particular economic conditions will unfold, then it seems reasonable 
to hold a mix of assets that can perform well across all different types of 
economic environments. Leverage helps make the impact of the asset 
classes similar.”
``` 
...quote from [Bridgewater’s All-Weather Story][2])

All-Weather is an approach to asset allocation designed to minimize downside but still perform regardless of the prevailing economic environment, hence the name “all-weather”.  The concept was first implemented by Ray Dalio and his team at Bridgewater Associates, now the largest hedge fund in the world. In researching and developing All-Weather, Bridgewater recognized there are primarily two factors driving the value of any asset class - the levels of economic activity (growth) and inflation. 

Therefore, the economy can be broadly viewed as having four “environments”. These are:

1. Rising growth 
2. Falling growth 
3. Rising inflation and
4. Falling inflation. 

(use [portfolio-settings.yaml](portfolio-settings.yaml) to assign tickers for each of these evironments)

Throughout history and across geographical regions, distinct asset classes have consistently performed well in each of these four environments. So, there is a season for all assets, but unlike the real weather  you never know which seasons are next or when the seasons will change, and worse, two seasons can occur at once! So surprises impact asset prices due to unexpected rises or falls in growth and inflation.

Recognizing this, an All-Weather portfolio essentially comprises four sub-portfolios - one for each economic environment containing assets known to perform well in that environment. Risk is then balanced equally within and between between each of the four environments (see [calculate-all-weather-ticker-weights.py](calculate-all-weather-ticker-weights.py) for risk balancing with and between environments).

An **important point** to clarify is that the all-weather-like portfolio weights produced by this repo are certainly NOT the same as Bridgewater’s. *Bridgewater uses cheap leverage and sophisticated investment instruments to increase returns while still minimizing risk in their All Weather product.* The code in this repo does not currently account for leverage and will thus produce portfolios with considerably lower expected returns...but they'll still do a good job at minimizing drawdowns if appropriate tickers are assigned in [portfolio-settings.yaml](portfolio-settings.yaml). 

Still working on how the average individual investor can cost-effectively leverage the lower volatility assets (e.g. Treasury bonds) to have the same volatility as equities, thus maintaining risk parity while increasing returns, like Bridgewater can. It will be relatively easy to adapt the code in this repo to accomidate the use of leverage, but the difficult part is finding a way to get cheap leverage that costs as close the risk free interest rate as possible. One way might be through Treasury bond futures. If you have the answer of how to practically do this, expicially for Aussie Treasury bonds, please let me know!

[1]: https://www.alphavantage.co/support/#api-key
[2]: https://www.bridgewater.com/resources/all-weather-story.pdf
