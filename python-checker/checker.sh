#!/usr/bin/env bash

if [ ! -z $2 ]; then 
    strict=true
fi

checker_location=$(pwd)
cd $1

find . -type f -iname "package.xml" -print0 | while IFS= read -r -d $'\0' line; do
    dir=${line%"package.xml"}
    cd $dir

    if [ "$(uname)" == "Darwin" ]; then    
        ggrep -o -P '(?<=<run_depend>).*(?=</run_depend>)' package.xml > requirements.txt
        ggrep -o -P '(?<=<exec_depend>).*(?=</exec_depend>)' package.xml > requirements.txt
        ggrep -o -P '(?<=<name>).*(?=</name>)' package.xml > requirements.txt
    else 
        grep -o -P '(?<=<run_depend>).*(?=</run_depend>)' package.xml > requirements.txt
        grep -o -P '(?<=<exec_depend>).*(?=</exec_depend>)' package.xml > requirements.txt
        grep -o -P '(?<=<name>).*(?=</name>)' package.xml > requirements.txt
    fi
    
    cat $checker_location/built-in_rospack_packages.txt >> requirements.txt
    cat $checker_location/built-in_pip_packages.txt >> requirements.txt

    if [ "$(uname)" == "Darwin" ]; then
        if [ "$strict" == true ]; then 
     		echo "Running in strict mode"
			ggrep -F -v -f <(find . -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | ggrep -v 'src' | ggrep -v '\.') <(flake8 --select=I900 | ggrep -v 'msg')
        else
            flake8 --select=I900 | ggrep -v 'msg'
        fi
    else
        if [ "$strict" == true ]; then 
        	echo "Running in strict mode"
            grep -F -v -f <(find -type f -name "*.py" | sed 's|/[^/]*$||' | sed 's|.*/||' | grep -v 'src' | grep -v '\.') <(flake8 --select=I900 | grep -v 'msg')
        else
            flake8 --select=I900 | ggrep -v 'msg'
        fi
    fi
    
    rm requirements.txt
    cd ..

done