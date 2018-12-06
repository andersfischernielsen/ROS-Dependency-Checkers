#!/usr/bin/env bash
cd $1
echo pwd

git checkout HEAD~
while [ $? -ne 128 ]; do
    git checkout HEAD~
    ../../../checker.py .
done