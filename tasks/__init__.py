"""Add format and test to collections."""

from __future__ import annotations

from invoke import Collection

from . import docs, test

ns = Collection()
ns.add_collection(test)
ns.add_collection(docs)
