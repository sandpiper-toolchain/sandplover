.. sandplover documentation master file

************
sandplover
************

.. image:: https://github.com/sandpiper-toolchain/sandplover/workflows/build/badge.svg
  :target: https://github.com/sandpiper-toolchain/sandplover/actions

.. image:: https://codecov.io/gh/sandpiper-toolchain/sandplover/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/sandpiper-toolchain/sandplover

*sandplover* is a Python package for manipulating depositional system data cubes.
The package has robust objects and routines designed to help organize, visualize, and analyze topography and sedimentological timeseries data.
*sandplover* works especially well with data from deltaic systems (e.g., the `pyDeltaRCM numerical model <https://github.com/DeltaRCM/pyDeltaRCM>`_  and laboratory delta experiments).

.. plot:: guides/cover.py

   A :obj:`~sandplover.plan.Planform` view of bed elevation in a modeled deltaic deposit, and a cross-:obj:`~sandplover.section.StrikeSection` view of sediment deposition timing in stratigraphy.


sandplover documentation
#########################################


.. image:: https://img.shields.io/static/v1?label=GitHub&logo=github&message=source&color=brightgreen
    :target: https://github.com/sandpiper-toolchain/sandplover

.. image:: https://badge.fury.io/gh/sandpiper-toolchain%2Fsandplover.svg
    :target: https://github.com/sandpiper-toolchain/sandplover/releases

Documentation Table of Contents
-------------------------------

.. toctree::
   :maxdepth: 1

   meta/installing
   meta/contributing
   meta/license
   meta/conduct
   meta/planning

.. toctree::
   :maxdepth: 1

   guides/10min

.. toctree::
   :maxdepth: 2

   guides/userguide
   guides/examples/index
   guides/subject_guides/index
   guides/devguide


.. toctree::
   :maxdepth: 2

   reference/index


Project status
##############

sandplover is currently in development, so the API is not *guaranteed* to be stable between versions; we do make an effort to maintain backwards compatibility.
This open-source software is made available without warranty or guarantee of accuracy or correctness.
