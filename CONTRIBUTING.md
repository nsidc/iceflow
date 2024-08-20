See the [Scientific Python Developer Guide][spc-dev-intro] for a detailed
description of best practices for developing scientific packages.

[spc-dev-intro]: https://learn.scientific-python.org/development/

# Setting up a development environment

You can set up a development environment with `conda` or your environment
manager of choice:

```bash
conda create -n iceflow-dev pip
conda activate iceflow-dev
pip install --editable .[dev]
```

# Pre-commit

You should prepare pre-commit, which will help you by checking that commits pass
required checks:

```bash
pre-commit install # Will install a pre-commit hook into the git repo
```

You can also/alternatively run `pre-commit run` (changes only) or
`pre-commit run --all-files` to check without installing the hook.

# Common tasks

Common dev tasks are handled by [invoke](https://www.pyinvoke.org/). To see
available tasks:

```
$ inv -l
Available tasks:

  test.all (test)              Run all of the tests.
  test.pytest                  Run all tests with pytest.
  test.typecheck (test.mypy)   Run mypy typechecking.
```

# Releasing

To release a new version of the software, first update the CHANGELOG.md to
reflect the version you plan to release. Then, bump the version with
[bump-by-version](https://github.com/callowayproject/bump-my-version):

```
$ bump-my-version bump {major|minor|patch}
```

This will update files containing the software version number.

> [!WARNING]
>
> Please do not attempt to update version numbers by hand!

Commit these changes and, once ready, merge them into `main` (through the use of
a Pull Request on a feature branch). Tag the commit you want to release on
`main` to initiate a GitHub Action (GHA) that will release the package to
anaconda.org.
