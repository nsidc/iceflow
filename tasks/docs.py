from __future__ import annotations

from invoke import task

from .util import PROJECT_DIR, print_and_run


@task()
def build(_ctx):
    """Build docs."""
    # (re)generate the api docs
    print_and_run(
        (
            f"sphinx-apidoc -o {PROJECT_DIR}/docs/api/ --no-toc"
            f" --module-first --implicit-namespaces --force {PROJECT_DIR}/src/nsidc"
        ),
        pty=True,
    )

    # Build the docs
    print_and_run(
        (
            "sphinx-build --keep-going -n -T -b=html"
            f" {PROJECT_DIR}/docs {PROJECT_DIR}/docs/_build/html/"
        ),
        pty=True,
    )
