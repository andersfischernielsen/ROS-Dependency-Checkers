#!/usr/bin/env bash

strict=false
if [ ! -z $2 ]; then 
    strict=true
    echo "Running in strict mode"
fi

checker_location=$(pwd)
cd $1

find . -type f -iname "package.xml" -print0 | while IFS= read -r -d $'\0' line; do
    ggrep -o -P '(?<=<run_depend>).*(?=</run_depend>)' $line > requirements.txt
    cat $checker_location/built-in_rospack_packages.txt >> requirements.txt
    cat $checker_location/built-in_pip_packages.txt >> requirements.txt

    if [ "$(uname)" == "Darwin" ]; then
        if [ "$strict"==true ]; then 
            ggrep -F -v -f <(find . -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | ggrep -v 'src' | ggrep -v '\.') <(flake8 --select=I900 | ggrep -v 'msg')
        else
            flake8 --select=I900 | ggrep -v 'msg'
        fi
    else
        if [ "$strict"==true ]; then 
            grep -F -v -f <(find -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | grep -v 'src' | grep -v '\.') <(flake8 --select=I900 | grep -v 'msg')
        else
            flake8 --select=I900 | ggrep -v 'msg'
        fi
    fi

    rm requirements.txt 
done