# @Author: George Onoufriou <archer>
# @Date:   2021-07-27T14:02:55+01:00
# @Last modified by:   archer
# @Last modified time: 2021-07-27T16:00:16+01:00

import time
import unittest
import numpy as np

from fhez.nn.optimiser.adam import Adam
from fhez.rearray import ReArray as Erray  # aliasing for later adjust


class AdamTest(unittest.TestCase):
    """Test Adaptive Moment optimizer."""

    def setUp(self):
        """Start timer and init variables."""
        self.start_time = time.time()

    def tearDown(self):
        """Calculate and print time delta."""
        t = time.time() - self.start_time
        print('%s: %.3f' % (self.id(), t))

    def linear(self, x, m, c):
        """Calculate standard linear function for testing against."""
        return (m * x) + c

    def test_init(self):
        """Check Adam can be initialised using defaults."""
        optimiser = Adam()
        self.assertIsInstance(optimiser, Adam)
        self.assertIsInstance(optimiser.S_d, dict)
        self.assertIsInstance(optimiser.V_d, dict)
        self.assertIsInstance(optimiser.alpha, float)
        self.assertIsInstance(optimiser.beta_1, float)
        self.assertIsInstance(optimiser.beta_2, float)
        self.assertIsInstance(optimiser.epsilon, float)

    def test_update_linear(self):
        """Check adam update/ optimisation."""
        optimiser = Adam()
        x = 1
        parameters = {
            "m": 2,
            "c": 3,
        }
        truth = {
            "m": 6,
            "c": 7,
        }
        # calculate linear result
        y_hat = self.linear(x=x, m=parameters["m"], c=parameters["c"])
        # calculate desired result
        y = self.linear(x=x, m=truth["m"], c=truth["c"])
        loss = y - y_hat
        gradients = {
            "dfdm": x * loss,
            "dfdc": 1 * loss,
        }
        update = optimiser.optimise(parms=parameters, grads=gradients)
        self.assertIsInstance(update, dict)
        print(update)
        # check keys all still exist
        self.assertEqual(update.keys(), parameters.keys())
        # check there has been some update/ change that they are different
        self.assertNotEqual(update, parameters)
