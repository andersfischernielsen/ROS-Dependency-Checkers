#!/usr/bin/env bash

git checkout HEAD~
while [ $? -ne 128 ]; do
    git checkout HEAD~
    ./checker.js .
done