#!/usr/bin/env bash

for D in *; do [ -d "${D}" ] && echo "Checking $D" && ./../../dist/checker.js $D; done