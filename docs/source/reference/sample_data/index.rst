.. api.sample_data:

*********************************
Sample data
*********************************

The package includes several sample data sets to show how to interact with the
API. You do not *need* to get your data into the same format as these data, but
doing so will likely make it simpler to use sandplover, and to get the most
benefit from the tools included here.

The sample data are defined in ``sandplover.sample_data``.

.. currentmodule:: sandplover.sample_data

The sample data cubes can be accessed as, for example:

.. doctest::

    >>> import sandplover as spl
    >>> golfcube = spl.sample_data.golf()

.. note::

    Data is handled by `pooch` and will be downloaded and cached on local
    computer as needed.


Available information on the data cubes is enumerated in the following
section.


Example data cubes
------------------

.. autofunction:: golf
.. autofunction:: xslope
.. autofunction:: aeolian
.. autofunction:: landsat
.. autofunction:: rcm8
.. autofunction:: savi2020


Paths to data files
"""""""""""""""""""

.. note::

	The file path to each sample data cube can be accessed by a call to
	`sample_data._get_xxxxxx_path()`  for the corresponding data set.

.. code::

    >>> spl.sample_data._get_golf_path()
    '<cache-path>/sandplover/golf.zip.unzip/pyDeltaRCM_output.nc'
