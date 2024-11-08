<p align="center">
  <img alt="NSIDC logo" src="https://nsidc.org/themes/custom/nsidc/logo.svg" width="150" />
</p>

# Iceflow Python Library

<!-- prettier-ignore -->
> [!WARNING]
> This repository is under active development. Major changes to the structure of
> this repository and its code are expected. We are striving to develop code
> that is well-tested and peer-reviewed, but nothing contained here should be
> expected to work correctly (or at all!) in this early phase.

`iceflow` is a Python library that provides the ability to search, download, and
access laser altimetry data from (pre-)Operation Icebridge and ICESat datasets.
`iceflow` supports the following datasets:

| Dataset                                                  | Temporal Coverage             |
| -------------------------------------------------------- | ----------------------------- |
| [ILATM1B v1](https://nsidc.org/data/ilatm1b/versions/1)  | 2009-03-31 through 2012-11-08 |
| [ILATM1B v2](https://nsidc.org/data/ilatm1b/versions/2)  | 2013-03-20 through 2019-11-20 |
| [BLATM1B v1](https://nsidc.org/data/blatm1b/versions/1)  | 1993-06-23 through 2008-10-30 |
| [ILVIS2 v1](https://nsidc.org/data/ilvis2/versions/1)    | 2009-04-14 through 2015-10-31 |
| [ILVIS2 v2](https://nsidc.org/data/ilvis2/versions/2)    | 2017-08-25 through 2017-09-20 |
| [GLAH06 v034](https://nsidc.org/data/glah06/versions/34) | 2003-02-20 through 2009-10-11 |

## Level of Support

- This repository is not actively supported by NSIDC but we welcome issue
  submissions and pull requests in order to foster community contribution.

See the [LICENSE](./LICENSE) for details on permissions and warranties. Please
contact nsidc@nsidc.org for more information.

## Requirements

- [python](https://www.python.org/) >=3.10
- [Earthdata Login account](https://urs.earthdata.nasa.gov/)

## Usage

### Install

```bash
pip install nsidc-iceflow
```

### Using `iceflow`

```python
from nsidc import iceflow

# TODO
```

## Credit

This content was developed by the National Snow and Ice Data Center with funding
from multiple sources.
