#!/bin/sh

# Script to run your program LOCALLY.

set -e # Exit early if any commands fail

# Copied from .codecrafters/run.sh

exec pipenv run python3 -m app.main "$@"