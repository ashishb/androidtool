#!/usr/bin/env bash
set -eou pipefail

# R = refactor
# C = convention
# W = warning

python3 -m pylint src/*.py release/setup.py --disable=R,C,W0603,E0602,W0511,W0406,W0621,W0601,W0612
