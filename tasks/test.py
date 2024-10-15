"""Task to run tests for this package."""

from __future__ import annotations

from invoke import task

from .util import PROJECT_DIR, print_and_run


@task(aliases=["mypy"])
def typecheck(_ctx):
    """Run mypy typechecking."""
    print_and_run(
        "mypy",
        pty=True,
    )

    print("🎉🦆 Type checking passed.")


@task()
def unit(_ctx):
    """Run all unit tests with pytest."""
    print_and_run(
        f"PYTHONPATH={PROJECT_DIR}/src:$PYTHONPATH pytest tests/unit/ --capture=no",
        pty=True,
    )


@task()
def integration(_ctx):
    """Run integration tests with pytest."""
    print_and_run(
        f"PYTHONPATH={PROJECT_DIR}/src:$PYTHONPATH pytest tests/integration --capture=no",
        pty=True,
    )


@task()
def pytest(_ctx):
    """Run all tests with pytest."""
    print_and_run(
        f"PYTHONPATH={PROJECT_DIR}/src:$PYTHONPATH pytest tests/ --capture=no",
        pty=True,
    )


@task(pre=[typecheck, unit])
def ci(_ctx):
    """Run all CI tests"""


@task(
    pre=[
        typecheck,
        pytest,
    ],
    default=True,
)
def all(_ctx):
    """Run all of the tests."""
