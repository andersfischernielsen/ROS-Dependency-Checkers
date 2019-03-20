#!/usr/bin/env python3

from catkin.find_in_workspaces import find_in_workspaces
import os
import sys
import xml.etree.ElementTree as ET
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
            file = open(p.strip(), 'r')
            tree = ET.fromstring(file.read())
            includes = tree.findall('*/include')
            for include in includes:
                regex = re.compile(r'(\$\(find )(.*)\)', re.IGNORECASE)
                package = regex.match(include.attrib['file']).groups()[1]
                if (not exists_in_workspace(package, package_path) and package not in pip and package not in rospack):
                    error_packages.append(package)

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


if (len(sys.argv) > 1):
    print(f"Checking {sys.argv[1]}")
    errors = find_launch_dependencies(sys.argv[1])
    print("Errors found:")
    for error in errors:
        print(f"\t{error}")
