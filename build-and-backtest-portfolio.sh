#!/usr/bin/env sh

if [ -z "$ALPHAVANTAGE_KEY" ]; then
    echo "\$ALPHAVANTAGE_KEY must be set, quitting"
    exit 1
fi

set -o errexit

python3 -m unittest discover -v -s ./tests
python3 get-ticker-time-series.py
python3 calculate-all-weather-ticker-weights.py
python3 assess-portfolio-historic-performance.py
