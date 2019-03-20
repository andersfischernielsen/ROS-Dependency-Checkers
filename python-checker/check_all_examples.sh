#!/usr/bin/env bash

for D in Examples/rosdistro/*; do [ -d "${D}" ] && echo "Checking $D" && ./checker.sh $D; done