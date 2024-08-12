See the [Scientific Python Developer Guide][spc-dev-intro] for a detailed
description of best practices for developing scientific packages.

[spc-dev-intro]: https://learn.scientific-python.org/development/

# Setting up a development environment

You can set up a development environment by running:

```bash
conda env create -f environment.yml
```

# Pre-commit

You should prepare pre-commit, which will help you by checking that commits pass
required checks:

```bash
pip install pre-commit # or brew install pre-commit on macOS
pre-commit install # Will install a pre-commit hook into the git repo
```

You can also/alternatively run `pre-commit run` (changes only) or
`pre-commit run --all-files` to check even without installing the hook.

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
