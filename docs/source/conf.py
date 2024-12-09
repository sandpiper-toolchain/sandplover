# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import importlib
import os
import sys


def get_version_from_file(path_to_version_file: str) -> str:
    spec = importlib.util.spec_from_file_location("_version", path_to_version_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.__version__


src_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
)

# -- Project information -----------------------------------------------------

project = 'DeltaMetrics'
copyright = '2020, The DeltaRCM Team'
author = 'The DeltaRCM Team'

__version__ = get_version_from_file(
    os.path.join(src_dir, "deltametrics", "_version.py")
)

# The full version, including alpha/beta/rc tags
release = __version__
version = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.autosummary',
              'sphinx.ext.napoleon',
              'sphinx.ext.graphviz',
              'sphinx.ext.mathjax',
              'sphinx.ext.githubpages',
              'matplotlib.sphinxext.plot_directive',
              'sphinx.ext.todo']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Napoleon settings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Autosummary / Automodapi settings
autosummary_generate = True
automodapi_inheritance_diagram = False
autodoc_default_options = {'members': True, 'inherited-members': True,
                           'private-members': False}

# doctest
doctest_global_setup = '''
import deltametrics as dm
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
'''

# empty string disables testing all code in any docstring
doctest_test_doctest_blocks = ''  

# mpl plots
plot_basedir = 'pyplots'
plot_html_show_source_link = True
plot_include_source = True
plot_formats = ['png', ('hires.png', 300)]
plot_pre_code = '''
import numpy as np
from matplotlib import pyplot as plt
import deltametrics as dm
'''

# img math
# imgmath_latex_preamble = '\\usepackage{fouriernc}' # newtxsf, mathptmx

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinxdoc'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
