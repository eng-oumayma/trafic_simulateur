"""Configuration Sphinx du simulateur de trafic."""
import os
import sys

sys.path.insert(0, os.path.abspath(".."))   # racine du projet

project = "Simulateur de trafic"
author = "Équipe Mobilité Intelligente"
from core import __version__  # noqa: E402

release = __version__
version = ".".join(__version__.split(".")[:2])
language = "fr"

extensions = [
    "sphinx.ext.autodoc",      # documentation à partir des docstrings
    "sphinx.ext.napoleon",     # docstrings style Google
    "sphinx.ext.viewcode",     # liens vers le code source
    "sphinx.ext.autosummary",  # tableaux récapitulatifs
]

autosummary_generate = False
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": "__init__",
}
napoleon_google_docstring = True
napoleon_use_ivar = True

try:
    import sphinx_rtd_theme  # noqa: F401
    html_theme = "sphinx_rtd_theme"
except ImportError:
    html_theme = "alabaster"
html_static_path = ["_static"]
exclude_patterns = ["_build"]
