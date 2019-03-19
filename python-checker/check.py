#!/usr/bin/env bash

grep -o -P '(?<=<run_depend>).*(?=</run_depend>)' package.xml > requirements.txt
cat built-in_rospack_packages.txt >> requirements.txt
cat built-in_pip_packages.txt >> requirements.txt
flake8 --select=I900