# Create all-weather risk parity weights and back-test

WORK IN PROGRESS - _I plan to make a docker container for this eventually, but until then, follow the steps below_

## Overview 
These scripts takes as input the users’ desired assets which the user has already pre-assigned into their relevant "environments" in the [portfolio-settings.yaml](portfolio-settings.yaml) file. 

- e.g. equities go in the 'rising growth' and the 'falling inflation' environments because that's when they tend to do well, IL-bonds assigned to the 'rising inflation' and 'falling growth' environments, etc.

The algorithm then: 

1. creates weights for risk-parity of the user's assets *within* each environment, essentially creating 4 "sub-portfolios", a sub-portfolio for each environment. Then it, 
2. looks at the overall volatility of each sub-portfolio and creates risk-parity weights *between* each of the 4 sub-portfolios so each takes on 25% of the risk. Then, 
3. each asset’s final weight is determined by the sum of [its within environment weights]-multiplied by-[its overall environment weights], and the final ticker weights are output, along with historical performance simulations of a portfolio based on the final ticker weights. 

The *within-* and *between-environment* risk-parity calculations are performed with the help of a `python` version of the [riskParityPortfolio][5] package by [Ze Vinicius][3] and [Daniel Palomar][4]. See [a nice vignette here][8] for the `riskParityPortfolio` package - I use the "**basic convex formulation**", which was based on [Spinu (2013)][7]'s unique solution].

## Dependencies 
- [requirements.txt](/requirements.txt)
- python3.7

## How to use:

1. `git clone git@github.com:DanielPNewman/all-weather-risk-parity.git`
2. `cd all-weather-risk-parity`
3. `pip3 install -r requirements.txt` 
4. Set up git lfs `git lfs install` then `git lfs track '*.csv'`
3. Get a free [alphavantage API key here][1] and set the key as environment variable: *ALPHAVANTAGE_KEY*
4. Set your desired portfolio and benchmark tickers in the [portfolio-settings.yaml](/portfolio-settings.yaml) file. 
	- Make sure the tickers you use have enough historical data (e.g. at least 7 years) available for volatility estimates. 
5. Run `./build-and-backtest-portfolio.sh` which executes the following scripts:
	- [get-ticker-time-series.py](/get-ticker-time-series.py)
	- [calculate-all-weather-ticker-weights.py](/calculate-all-weather-ticker-weights.py)
	- [assess-portfolio-historic-performance.py](/assess-portfolio-historic-performance.py)

6. See your results, they will be written to the [results](/results) subdirectory, along with a named copy of the `portfolio-settings` file related to each set of results.  

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

Recognizing this, an All-Weather portfolio essentially comprises four sub-portfolios - one for each economic environment containing assets known to perform well in that environment. Risk is then balanced equally within and between each of the four environments (see [calculate-all-weather-ticker-weights.py](calculate-all-weather-ticker-weights.py) for risk balancing with and between environments).

An **important point** to clarify is that the all-weather-like portfolio weights produced by this repo are certainly NOT the same as Bridgewater’s. *Bridgewater uses cheap leverage and sophisticated investment instruments to increase returns while still minimizing risk in their All Weather product.* The code in this repo does not currently account for leverage and will thus produce portfolios with considerably lower expected returns...but they should still do a good job at reducing the size of drawdowns if one assigns appropriate tickers in [portfolio-settings.yaml](portfolio-settings.yaml). 

Still working on how the average individual investor can cost-effectively leverage the lower volatility assets (e.g. Treasury bonds) to have the same volatility as equities, thus maintaining risk parity while increasing returns, like Bridgewater can. It will be relatively easy to adapt the code in this repo to accomidate the use of leverage, but the difficult part is finding a way to get cheap leverage that costs as close the risk free interest rate as possible. One way might be through Treasury bond futures. If you have the answer of how to practically do this, expicially for Aussie Treasury bonds, please let me know!

Also, nobody is suggesting the kind of simple All-Weather portfolios produced with the help of this repo are optimal or will maximize returns. They almost certainly won’t! Rather, the design is to protect assets by avoiding large drawdowns during economic upheavals and market downturns, while still providing reasonable returns above the cash interest rate.



## Licence
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

Licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)

## Disclaimer
The information, software, and any additional resources contained in this repository are not intended as, and shall not be understood or construed as, financial advice. Past performance is not a reliable indicator of future results and investors may not recover the full amount invested. The authors of this repository accept no liability whatsoever for any loss or damage you may incur. Any opinions expressed in this repository are from the personal research and experience of the authors and are intended as educational material.

[1]: https://www.alphavantage.co/support/#api-key
[2]: https://www.bridgewater.com/resources/all-weather-story.pdf
[3]: http://mirca.github.io/
[4]: http://www.danielppalomar.com/
[5]: https://github.com/dppalomar/riskParityPortfolio
[6]: https://github.com/dppalomar/riskparity.py
[7]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2297383
[8]: https://cran.r-project.org/web/packages/riskParityPortfolio/vignettes/RiskParityPortfolio.html
