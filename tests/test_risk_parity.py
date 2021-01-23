import numpy as np
import pandas as pd
from utils import (calc_risk_parity_weights)
import unittest


class TestRiskParity(unittest.TestCase):

    def setUp(self):

        # create a dafaframe, "simulated_returns", with the first asset "one"...
        simulated_returns = pd.DataFrame({'one': np.random.normal(loc=3, scale=10, size=15000)})
        # and then 3 other assets...
        simulated_returns['two'] = simulated_returns.one*2  # ...with exactly 2x it's volatility,
        simulated_returns['three'] = simulated_returns.one*3  # ...exactly 3x it's volatility,
        simulated_returns['four'] = simulated_returns.one*4  # ...and exactly 4x it's volatility.

        # now get the covariance matrix for input into calc_risk_parity_weights():
        cov = simulated_returns.cov().to_numpy()

        # get the risk parity weights for each of the 4 assets
        weights, _ = calc_risk_parity_weights(cov)

        self.weights = weights

    def test_relative_weights(self):
        weight_one = self.weights[0]
        weight_two = self.weights[1]
        weight_three = self.weights[2]
        weight_four = self.weights[3]

        # one should be 2x the weight of two
        self.assertAlmostEqual(2/1, weight_one/weight_two)
        # one should be 3x the weight of three
        self.assertAlmostEqual(3/1, weight_one/weight_three)
        # one should be 4x the weight of four
        self.assertAlmostEqual(4/1, weight_one/weight_four)
        # two should be 2x the weight of four
        self.assertAlmostEqual(2/1, weight_two/weight_four)
        # two should be 1.5x the weight of three
        self.assertAlmostEqual(3/2, weight_two/weight_three)
        # three should be given 1.333'x times the weight of 4
        self.assertAlmostEqual(4/3, weight_three/weight_four)
