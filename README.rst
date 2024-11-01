Introduction
==================

NWB data validator performs Quality assurance & quality control on the NWB (`Neurodata Without Borders <https://www.nwb.org/>`_) files converted from the `IGOR format <https://en.wikipedia.org/wiki/IGOR_Pro>`_.
A report is generated after the validation to inform on the results.
The report contains only the validation & verification failures for the NWB files in the
batch.


Installation
------------

Clone the repository first.

.. code-block:: console

    git clone git@github.com:BlueBrain/lnmc-nwb-conversion-validator.git

Then go to the project directory where setup.py is contained and run the command below to install the package.

.. code-block:: console

    $ pip install .


Usage
--------

See `batch_validation.py` and `test_validation.py` for usage examples. Check the API documentation for further information on usage.


Funding & Acknowledgements
--------------

The development and maintenance of this code is supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.


Copyright
---------

Copyright (c) 2024 Blue Brain Project/EPFL

This work is licensed under `Apache 2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`_
