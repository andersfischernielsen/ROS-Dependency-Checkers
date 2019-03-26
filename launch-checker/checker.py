#!/usr/bin/env python3

from catkin.find_in_workspaces import find_in_workspaces
import os
import sys
from lxml import etree
import re
import rospkg


pip = list(map(lambda package: package.strip(), open(
    'built-in_pip_packages.txt', 'r').readlines()))
rospack = list(map(lambda package: package.strip(), open(
    'built-in_rospack_packages.txt', 'r').readlines()))


def find_launch_dependencies(path):
    error_packages = []
    packages = os.popen(
        f'find {path} -type f -name "package.xml"').readlines()
    for package in packages:
        package_path = package.replace('package.xml', '').strip()
        paths = os.popen(
            f"find {package_path} -type f -name '*.launch'").readlines()

        for p in paths:
            tree = etree.parse(p.strip())
            includes = tree.xpath('//include/@file')
            for include in includes:
                regex = re.compile(r'(\$\(find )(.*)\)', re.IGNORECASE)
                match = regex.match(include)
                if (len(match.regs) is 3 and not exists_in_workspace(package, package_path) and package not in pip and package not in rospack):
                    error_packages.append(match[2])

    return error_packages


def exists_in_workspace(package, package_path):
    rp = _get_rospack()
    rospack_path = None
    try:
        rospack_path = rp.get_path(package)
        return rospack_path
    except:
        source_paths = find_in_workspaces(
            ['libexec'], project=package, first_matching_workspace_only=True,
            source_path_to_packages=package_path)
        return rospack_path or source_paths


def _get_rospack():
    return rospkg.RosPack()


if sys.gettrace() is not None:
    print('Running in DEBUG')
    errors = find_launch_dependencies('Examples/MWE/')

if (len(sys.argv) > 1):
    print(f"Checking {sys.argv[1]}")
    errors = find_launch_dependencies(sys.argv[1])
    print("Errors found:")
    for error in errors:
        print(f"\t{error}")
