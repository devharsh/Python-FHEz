#!/usr/bin/env python3

# @Author: GeorgeRaven <archer>
# @Date:   2020-09-16T11:33:51+01:00
# @Last modified by:   archer
# @Last modified time: 2021-08-11T15:47:59+01:00
# @License: please see LICENSE file in project root

import logging as logger
import numpy as np
import unittest
import copy

from tqdm import tqdm

import seal
from fhez.rearray import ReArray
from fhez.nn.layer.layer import Layer


class Layer_CNN(Layer):

    @Layer.fwd
    def forward(self, x: (np.array, ReArray)):
        """Take lst of batches of x, return activated output lst of layer."""

        # stride over x using our convolutional filter
        # lets say x = (64, 32, 32, 3) or x_1D = (3, 100, 1, 8)
        # also could be x = (64, 32, 32, crypt), x = (3, 100, 1, crypt)
        # and filter is (32, 3, 3, 3) or x_1D = (1, 100, 1, 8)

        # if no cross correlation windows have been specified create them
        # and cache them for later re-use as uneccessary to re-compute
        if self.windows is None:
            self.windows = self.windex(data=x.shape[1:],
                                       filter=self.weights.shape[1:],
                                       stride=self.stride[1:])
            self.windows = list(map(self.windex_to_slice, self.windows))

        activated = []
        # apply each window and do it by index so can state progress
        for i in tqdm(range(len(self.windows)), desc="{}.{}".format(
                self.__class__.__name__, "forward"),
            ncols=80, colour="blue"
        ):
            # create a primer for application of window without having to
            # modify x but instead the filter itself
            cc_primer = np.zeros(x.shape[1:])
            # now we have a sparse vectore that can be used to convolve
            cc_primer[self.windows[i]] = self.weights
            t = cc_primer * x
            t = t + (self.bias/(t.size/len(t)))  # commute addition before sum
            t = self.activation_function.forward(t)
            activated.append(t)
        return np.array(activated)

    @Layer.bwd
    def backward(self, gradient, x):
        """Calculate the local gradient of this CNN.

        Given the gradient that precedes us,
        what is the local gradient after us.
        """
        ag = gradient
        x = np.array(x)
        # calculate gradient with respect to cross correlation
        # df/dbias is easy as its addition so its same as previous gradient
        self.bias_gradient = gradient * 1  # uneccessary but here for clarity
        # gradient from a CNN can be from multiple outputs so need to avg
        # the batches then sum the gradients that remain
        self.bias_gradient = np.sum(np.sum(self.bias_gradient, axis=1) /
                                    self.bias_gradient.shape[1], axis=0)
        # for each window slice apply window to cached x to find what weights
        # were multiplied against
        per_batch_windows = []
        for i in tqdm(range(len(self.windows)), desc="{}.{}".format(
                self.__class__.__name__, "backward-window"),
            ncols=80, colour="blue"
        ):
            batch_window = np.array(
                list(map(lambda a: a[self.windows[i]], x)))
            per_batch_windows.append(batch_window)
        windows = np.array(per_batch_windows)

        # calculate weight gradient by expanding the gradient dims to match
        # the window dims so they can be broadcast then sum them allong the
        # number of filters axis
        t = gradient
        len_diff = len(windows.shape) - len(gradient.shape)
        # expand the dimensions of the ndarray according to the difference
        for i in range(len_diff):
            t = np.expand_dims(t, axis=t.ndim)
        self.weights_gradients = (windows * t).sum(axis=0).mean(axis=0)

        # dont care as end of computational chain for now
        # TODO finish calculating gradient of inputs with respect to cc outputs
        # return local gradient
        df_dx = np.random.rand(len(x))
        return df_dx

    @property
    def windows(self):
        if self.cache.get("windows") is not None:
            return self.cache["windows"]

    @windows.setter
    def windows(self, windows):
        self.cache["windows"] = windows

    def windex(self, data: list, filter: list, stride: list,
               dimension: int = 0, partial: list = []):
        """
        Recursive window index or Windex.

        This function takes 3 lists; data, filter, and stride.
        Data is a regular multidimensional list, so in the case of a 32x32
        pixel image you would expect a list of shape (32,32,3) 3 being the RGB
        channels.
        Filter is the convolutional filter which we seek to find all windows of
        inside the data. So for data (32,32,3) a standard filter could be
        applied of shape (3,3,3).
        Stride is a 1 dimensional list representing the strides for each
        dimension, so a stride list such as [1,2,3] on data (32,32,3) and
        filter (3,3,3), would move the window 1 in the first 32 dimension,
        2 in the second 32 dim, and 3 in the 3 dimension.

        This function returns a 1D list of all windows, which are themselves
        lists.
        These windows are the same length as the number of dimensions, and each
        dimension consists of indexes with which to slice the original data to
        create the matrix with which to convolve (cross correlate).
        An example given: data.shape=(4,4), filter.shape=(2,2), stride=[1,1]

        .. code-block:: python

            list_of_window_indexes = [
                [[0, 1], [0, 1]], # 0th window
                [[0, 1], [1, 2]], # 1st window
                [[0, 1], [2, 3]], # ...
                [[1, 2], [0, 1]],
                [[1, 2], [1, 2]],
                [[1, 2], [2, 3]],
                [[2, 3], [0, 1]],
                [[2, 3], [1, 2]],
                [[2, 3], [2, 3]], # T_x-1 window
            ]

        We get the indexes rather than the actual data for two reasons:

        - we want to be able to cache this calculation and use it for
          homogenus data that could be streaming into a convolutional
          neural networks, cutting the time per epoch down.
        - we want to use pure list slicing so that we can work with non-
          standard data, E.G Fully Homomorphically Encrypted lists.
        """
        # get shapes of structural lists
        d_shape = data if isinstance(data, tuple) else self.probe_shape(
            data)
        f_shape = filter if isinstance(filter, tuple) else self.probe_shape(
            filter)
        # if we are not at the end/ last dimension
        if len(stride) > dimension:
            # creating a list matching dimension len so we can slice
            window_heads = list(range(d_shape[dimension]))
            # using dimension list to calculate strides using slicing
            window_heads = window_heads[::stride[dimension]]
            # creating window container to hold each respective window
            windows = []
            # iterate through first index/ head of window
            for window_head in window_heads:
                # copy partial window up till now to branch it to mutliple
                # windows
                current_partial_window = copy.deepcopy(partial)
                # create index range of window in this dimension
                window = list(range(window_head, window_head +
                                    f_shape[dimension]))
                # if window end "-1" is within data bounds
                if (window[-1]) < d_shape[dimension]:
                    # add this dimensions window indexes to partial
                    current_partial_window.append(window)
                    # pass partial to recurse and build it up further
                    subwindow = self.windex(data, filter, stride, dimension+1,
                                            current_partial_window)
                    # logger.debug("subwindow {}: {}".format(dimension,
                    #                                        subwindow))
                    # since we want to create a flat list we want to extend if
                    # the list is still building the partial window or append
                    # if concatenating the partial windows to a single list
                    if (len(stride)-1) > dimension:
                        windows.extend(subwindow)
                    else:
                        windows.append(subwindow)
                else:
                    # discarding illegal windows that are out of bounds
                    pass
            return windows
        else:
            # this is the end of the sequence, can do no more so return
            return partial

    def windex_to_slice(self, window):
        """Convert x sides of window expression into slices to slice np."""
        slicedex = ()
        for dimension in window:
            t = (slice(dimension[0], dimension[-1]+1),)
            slicedex += t
        return slicedex
