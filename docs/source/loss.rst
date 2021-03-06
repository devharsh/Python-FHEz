.. include:: substitutions

.. _section_losses:

Loss Functions
==============

Loss functions are responsible for calculating some measure of wrongness. We usually use these to inform the neural network and us, just how good or bad our predictions :math:`\hat{y}` are compared to the ground truth :math:`y`.

.. csv-table:: Loss Functions Status
  :file: /losses/status.csv
  :header-rows: 1

.. toctree::
  :glob:
  :maxdepth: 3
  :caption: Loss Functions

  /losses/*

Loss Abstraction
################

.. automodule:: fhez.nn.loss.loss
  :members:
