#!/usr/bin/env bash

for D in Examples/rosdistro/*/; do [ -d "${D}" ] && ./checker.py $D; done