import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "starknet-abi"
copyright = "2024, Nethermind"
author = "Nethermind"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
]

autosummary_generate = True
autodoc_member_order = "groupwise"
autoclass_content = "class"
autodoc_class_signature = "separated"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_title = "Starknet ABI Documentation"
html_theme_options = {
    "show_toc_level": 2,
    "logo": {
        "image_light": "_static/logo-light.svg",
        "image_dark": "_static/logo-dark.svg",
        "link": "https://nethermind.io",
    },
    "use_repository_button": True,
    "repository_url": "https://github.com/nethermindEth/starknet-abi",
    "use_download_button": False,
    "home_page_in_toc": True,
}

html_static_path = ["_static"]
