"""Test deueue functionality."""
# @Author: George Onoufriou <archer>
# @Date:   2021-08-17T13:38:16+01:00
# @Last modified by:   archer
# @Last modified time: 2021-08-18T14:59:42+01:00

import time
import unittest
import numpy as np
from fhez.nn.operations.dequeue import Dequeue


class DequeueTest(unittest.TestCase):
    """Test dequeue operation node."""

    @property
    def data_shape(self):
        """Define desired data shape."""
        return (3, 32, 32, 3)

    @property
    def data(self):
        """Get some generated data."""
        array = np.random.rand(*self.data_shape)
        return array

    @property
    def reseal_args(self):
        """Get some reseal arguments for encryption."""
        return {
            "scheme": 2,  # seal.scheme_type.CKK,
            "poly_modulus_degree": 8192*2,  # 438
            # "coefficient_modulus": [60, 40, 40, 60],
            "coefficient_modulus":
                [45, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 45],
            "scale": pow(2.0, 30),
            "cache": True,
        }

    def setUp(self):
        """Start timer and init variables."""
        self.weights = (1,)  # if tuple allows cnn to initialise itself

        self.startTime = time.time()

    def tearDown(self):
        """Calculate and print time delta."""
        t = time.time() - self.startTime
        print('%s: %.3f' % (self.id(), t))

    def test_init(self):
        """Test enque initialisation."""
        Dequeue(length=10)

    def test_backward(self):
        """Check dequeue, queueing properly."""
        l = 10
        q = Dequeue(length=l)
        for i in range(l):
            out = q.backward(np.array([i]))
        self.assertNotEqual(out, None)
        truth = np.reshape(np.arange(l), (l, 1))
        np.testing.assert_array_almost_equal(out, truth,
                                             decimal=1,
                                             verbose=True)

    def test_forward(self):
        """Check gradients are mapped properly."""
        l = 10
        q = Dequeue(length=l)
        x = np.reshape(np.arange(l), (l, 1))
        dequeued = np.array(list(q.forward(x)))
        np.testing.assert_array_almost_equal(dequeued, x,
                                             decimal=1,
                                             verbose=True)
        # now checking yield of forward as iterator
        i = 0
        for deq in q.forward(x):
            np.testing.assert_array_almost_equal(deq, x[i],
                                                 decimal=1,
                                                 verbose=True)
            i += 1

        # for i in range(l):
        #     out = q.forward(np.array([i]))
        # self.assertNotEqual(out, None)
        # gradients = np.reshape(np.arange(l), (l, 1))
        # local_grad = np.array(list(q.backward(gradient=gradients)))
        # np.testing.assert_array_almost_equal(local_grad, gradients,
        #                                      decimal=1,
        #                                      verbose=True)
