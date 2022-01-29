#!/usr/bin/env sh

set -o errexit

python3 -m unittest discover -v -s ./tests
python3 get-ticker-time-series.py
python3 calculate-all-weather-ticker-weights.py
python3 assess-portfolio-historic-performance.py
