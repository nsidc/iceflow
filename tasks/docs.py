from __future__ import annotations

from invoke import task

from .util import PROJECT_DIR, print_and_run


def _build_apidocs_cmd():
    return (
        f"sphinx-apidoc -o {PROJECT_DIR}/docs/api/ --no-toc"
        f" --module-first --implicit-namespaces --force {PROJECT_DIR}/src/nsidc"
    )


@task()
def clean(_ctx):
    print_and_run(f"rm -rf {PROJECT_DIR}/docs/api/*")
    print_and_run(f"rm -rf {PROJECT_DIR}/docs/_build/*")


@task(pre=[clean])
def build(_ctx):
    """Build docs."""
    # (re)generate the api docs
    print_and_run(
        _build_apidocs_cmd(),
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


@task(pre=[clean])
def watch(_ctx):
    print_and_run(
        (
            f'sphinx-autobuild --pre-build "{_build_apidocs_cmd()}"'
            f" --watch {PROJECT_DIR}/src"
            f" --watch {PROJECT_DIR}/docs/notebooks"
            f" --ignore {PROJECT_DIR}/docs/notebooks/.ipynb_checkpoints"
            f" --ignore {PROJECT_DIR}/docs/notebooks/_sources"
            f" --ignore {PROJECT_DIR}/docs/notebooks/_static"
            f" --ignore {PROJECT_DIR}/docs/notebooks/downloaded-data/"
            f" {PROJECT_DIR}/docs {PROJECT_DIR}/docs/_build/html"
        ),
        pty=True,
    )
