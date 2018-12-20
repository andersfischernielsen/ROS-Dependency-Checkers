#!/usr/bin/env bash

for D in `find . -type d`
do
	cd $D
	git checkout HEAD~
	while [ "$?" -eq 0 ]; do
    	./../checker.js .
    	git checkout HEAD~
	done
done
