#!/usr/bin/env bash

for D in *; do [ -d "${D}" ] && echo "Checking $D" && ./../../checker.py $D; done