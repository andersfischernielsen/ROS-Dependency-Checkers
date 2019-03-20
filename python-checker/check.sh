#!/usr/bin/env bash

checker_location=$(pwd)
cd $1
ggrep -o -P '(?<=<run_depend>).*(?=</run_depend>)' package.xml > requirements.txt
cat $checker_location/built-in_rospack_packages.txt >> requirements.txt
cat $checker_location/built-in_pip_packages.txt >> requirements.txt

if [ "$(uname)" == "Darwin" ]; then
    ggrep -F -v -f <(find . -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | ggrep -v 'src' | ggrep -v '\.') <(flake8 --select=I900 | ggrep -v 'msg')
else
    grep -F -v -f <(find -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | grep -v 'src' | grep -v '\.') <(flake8 --select=I900 | grep -v 'msg')
fi

rm requirements.txt
