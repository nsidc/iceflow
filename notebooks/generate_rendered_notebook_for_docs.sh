#!/bin/bash

set -euxo pipefail

THIS_DIR="$( cd "$(dirname "$0")"; pwd -P )"

jupyter nbconvert --to notebook --execute --output="$THIS_DIR"/../docs/iceflow-example.ipynb "$THIS_DIR"/iceflow-example.ipynb
