#!/usr/bin/env bash

grep -o -P '(?<=<run_depend>).*(?=</run_depend>)' package.xml > requirements.txt
cat built-in_rospack_packages.txt >> requirements.txt
cat built-in_pip_packages.txt >> requirements.txt

grep -F -v -f <(find -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | grep -v 'src' | grep -v '\.') <(flake8 --select=I900 | grep -v 'msg')