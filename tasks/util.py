"""Utility routines."""

from __future__ import annotations

from pathlib import Path

from invoke import run

PROJECT_DIR = Path(__file__).parent.parent


def print_and_run(cmd, **run_kwargs):
    """Print the command string and then execute it."""
    print(cmd)
    kwargs = {
        "pty": True,
        **run_kwargs,
    }
    return run(cmd, **kwargs)
