# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------

project = 'nrtqclib'
copyright = '2026, Takaya Saito'
author = 'Takaya Saito'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'sphinx_tabs.tabs',
]
autodoc_typehints = "description"

# Cross-link the QC items, base classes and flag utilities that stay in aiqclib.
intersphinx_mapping = {
    'aiqclib': ('https://aiqclib.readthedocs.io/en/latest/', None),
}

# Keep curly quotes and ellipses, but never turn "--" / "---" into en/em
# dashes: the project does not use them anywhere.
smartquotes_action = "qe"

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
