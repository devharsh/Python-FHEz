# @Author: George Onoufriou <archer>
# @Date:   2021-07-27T14:02:55+01:00
# @Last modified by:   archer
# @Last modified time: 2021-09-10T14:51:43+01:00

import time
import unittest
import numpy as np
import marshmallow as mar

from fhez.nn.optimiser.adam import Adam
from fhez.nn.activation.linear import Linear
from fhez.nn.loss.mse import MSE


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
        self.assertIsInstance(optimiser.cache, dict)
        self.assertIsInstance(optimiser.alpha, float)
        self.assertIsInstance(optimiser.beta_1, float)
        self.assertIsInstance(optimiser.beta_2, float)
        self.assertIsInstance(optimiser.epsilon, float)

    @property
    def optimiser(self):
        return Adam()

    @property
    def x(self):
        return np.array([2])

    @property
    def nn(self):
        return Linear

    @property
    def lossfunc(self):
        return MSE

    def test_optimise(self):
        optimiser = self.optimiser
        x = self.x
        lossfunc = self.lossfunc()
        parameters = {
            "m": 0.4,
            "c": 0.5
        }
        truth = {
            "m": 0.402,
            "c": 0.5,
        }
        nn = self.nn(**parameters, optimiser=optimiser)
        nn_optimal = self.nn(**truth, optimiser=optimiser)
        y = nn_optimal.forward(x)

        for i in range(100):
            # get predicted and optimal output
            y_hat = nn.forward(x)
            # calculate the loss and gradient with respect to y_hat
            loss = lossfunc.forward(y=y, y_hat=y_hat)
            if i == 0:
                original_loss = loss
            dloss_y_hat = lossfunc.backward(loss)
            nn.backward(dloss_y_hat)
            nn.updates()  # this will now call adam to update its weights
        # print("Adam loss {}, originally {}".format(loss, original_loss))
        self.assertLess(loss, original_loss)

    def test_momentum(self):
        """Check Adam 1st moment operating properly, and updating vars."""
        # expresley setting variables so we can KNOW and answer to verify out
        beta_1 = 0.9
        optimiser = Adam(alpha=0.001,
                         beta_1=beta_1,
                         beta_2=0.999,
                         epsilon=1e-8)
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
        name = "m"
        m_hat = optimiser.momentum(gradient=gradients["dfd{}".format(name)],
                                   param_name=name)

        # check that internal state has been modified properly
        self.assertEqual(optimiser.cache[name]["t_m"], 2)
        m_true = (beta_1 * 0) + (1 - beta_1) * gradients["dfd{}".format(name)]
        self.assertEqual(optimiser.cache[name]["m"], m_true)
        # check it has returned a correct value
        m_hat_true = m_true / (1 - beta_1**1)
        self.assertEqual(m_hat, m_hat_true)

    def test_rmsprop(self):
        """Check Adam 2nd moment operating properly, and updating vars."""
        # expresley setting variables so we can KNOW and answer to verify out
        beta_1 = 0.9
        beta_2 = 0.999
        optimiser = Adam(alpha=0.001,
                         beta_1=beta_1,
                         beta_2=beta_2,
                         epsilon=1e-8)
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
        name = "m"
        v_hat = optimiser.rmsprop(gradient=gradients["dfd{}".format(name)],
                                  param_name=name)

        # check that internal state has been modified properly
        self.assertEqual(optimiser.cache[name]["t_v"], 2)
        m_true = (beta_1 * 0) + (1 - beta_2) * \
            gradients["dfd{}".format(name)] ** 2
        self.assertEqual(optimiser.cache[name]["v"], m_true)
        # check it has returned a correct value
        m_hat_true = m_true / (1 - beta_2**1)
        self.assertEqual(v_hat, m_hat_true)

    def test_getstate_setstate(self):
        """Check setstate getstate functionality."""
        obj_dump = Adam(alpha=0.002,
                        beta_1=0.8,
                        beta_2=0.998,
                        epsilon=1e-9)
        obj_load = Adam()
        # getting simple dictionary representation of class
        d = obj_dump.__getstate__()
        # check is dict properly
        self.assertIsInstance(d, dict)
        # check repr works properly returning a string
        self.assertIsInstance(repr(obj_dump), str)
        # recreate original object in new object
        obj_load.__setstate__(d)
        # check objects are equal
        self.assertTrue(obj_load.__dict__ == obj_dump.__dict__)
        # manually comparing each part of our dictionaries as we cant rely on
        # assertEqual to do the whole dictionary when it comes to multidim
        # numpy arrays
        for key, value in obj_dump.__dict__.items():
            if isinstance(value, np.ndarray):
                np.testing.assert_array_almost_equal(obj_dump.__dict__[key],
                                                     value,
                                                     decimal=1,
                                                     verbose=True)
            else:
                self.assertEqual(obj_dump.__dict__[key], value)
