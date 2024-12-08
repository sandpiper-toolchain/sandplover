#! /usr/bin/env python
from setuptools import setup, find_packages

from deltametrics._version import __version__

setup(
    name="DeltaMetrics",
    version=__version__,
    author="The DeltaRCM Team",
    license="MIT",
    description="Tools for manipulating sedimentologic data cubes.",
    long_description=open("README.rst").read(),
    packages=find_packages(exclude=["*.tests"]),
    package_data={"deltametrics.sample_data": ["registry.txt"]},
    include_package_data=True,
    url="https://github.com/DeltaRCM/DeltaMetrics",
    install_requires=[
        "matplotlib",
        "netCDF4",
        "h5netcdf",
        "scipy",
        "numpy",
        "pyyaml",
        "xarray",
        "pooch",
        "scikit-image",
        "numba",
        "h5py",
    ],
)
