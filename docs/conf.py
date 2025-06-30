from __future__ import annotations

import datetime as dt
import importlib.metadata
from typing import Any

project = "nsidc-iceflow"
copyright = f"{dt.date.today().year}, NSIDC"
author = "NSIDC"
version = release = importlib.metadata.version("nsidc-iceflow")

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"

html_theme_options: dict[str, Any] = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/NSIDC/nsidc-iceflow",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": "https://github.com/NSIDC/nsidc-iceflow",
    "source_branch": "main",
    "source_directory": "docs/",
}

myst_enable_extensions = [
    "colon_fence",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}


autodoc_mock_imports = [
    "pydantic*",
    "pandera*",
    "pandera.api",
]

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
    ("py:class", "pandera.typing.pandas.DataFrame"),
    ("py:class", "pydantic.main.BaseModel"),
    ("py:class", "pandera.api.pandas.model_config.BaseConfig"),
    ("py:class", "pandera.api.pandas.model.DataFrameModel"),
    ("py:class", "pandera.api.dataframe.model.Config"),
    # avoids warning:
    # `iceflow/docs/api/nsidc.iceflow.data.rst:13: WARNING: py:class reference target not found: data [ref.class]`
    ("py:class", "data"),
]

always_document_param_types = True

nb_execution_mode = "off"


def copy_notebook_images(app, _exception):
    """Copy notebook static images into place post-build."""
    import shutil
    from pathlib import Path

    source_dir = Path(app.srcdir) / "img"
    dest_dir = Path(app.outdir) / "img"

    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    shutil.copytree(source_dir, dest_dir)


def setup(app):
    """Setup build-finished action to copy images into place.

    Because the images are only referenced in jupyter notebooks, and not source
    files parsed directly by sphinx, the images will not be copied on their own.
    """
    app.connect("build-finished", copy_notebook_images)
