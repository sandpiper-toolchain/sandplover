.. api.plan:

*********************************
Planview operations
*********************************

The package makes available functions relating to planview operations on data.

The functions are defined in ``sandplover.plan``.

.. hint::

  There is a complete :doc:`Planform Subject Guide </guides/subject_guides/planform>` about the organization of this area of sandplover and examples for how to use and compute planform objects and metrics.


Planform types
==============

.. currentmodule:: sandplover.plan

.. rubric:: Basic data Planform

.. autosummary::
    :toctree: ../../_autosummary

    Planform

.. rubric:: Specialty Planforms

.. autosummary::
    :toctree: ../../_autosummary

    OpeningAnglePlanform
    MorphologicalPlanform

Functions
=========

.. autosummary::
    :toctree: ../../_autosummary

    compute_land_area
    compute_shoreline_roughness
    compute_shoreline_length
    compute_shoreline_distance
    compute_channel_width
    compute_channel_depth
    compute_surface_deposit_time
    compute_surface_deposit_age
    shaw_opening_angle_method
    morphological_closing_method
