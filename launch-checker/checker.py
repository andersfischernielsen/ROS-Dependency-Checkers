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
    error_packages = set()
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
                regex = re.compile(r'(\$\(find )(\w*)\)', re.IGNORECASE)
                match = regex.match(include)
                if not match or len(match.regs) is not 3:
                    continue
                dependency = match[2]
                if (not exists_in_workspace(dependency, package_path, packages) and dependency not in pip and dependency not in rospack):
                    error_packages.add(match[2])

    error_packages = list(error_packages)
    return error_packages


def exists_in_workspace(package, package_path, packages):
    metapackage_dependencies = parse_metapackage(packages)
    if package in metapackage_dependencies:
        return True

    rp = _get_rospack()
    rospack_path = None
    try:
        rospack_path = rp.get_path(package_path)
        return rospack_path
    except:
        source_paths = find_in_workspaces(
            ['libexec'], project=package_path, first_matching_workspace_only=True,
            source_path_to_packages=package_path)
        return rospack_path or source_paths


def parse_metapackage(packages):
    for package in packages:
        tree = etree.parse(package.strip())
        metapackage = tree.xpath('//metapackage')
        if metapackage:
            run_depends = tree.xpath('//run_depend')
            run_depends = list(map(lambda dep: dep.text, run_depends))
            return run_depends


def _get_rospack():
    return rospkg.RosPack()


def print_errors(errors):
    print("Errors found:")
    for error in errors:
        print(f"\t{error}")


if sys.gettrace() is not None:
    print('Running in DEBUG mode.')
    path = 'Examples/FULL/universal_robot/'
    print(f"Checking {path}")
    errors = find_launch_dependencies(path)
    print_errors(errors)

if (len(sys.argv) > 1):
    print(f"Checking {sys.argv[1]}")
    errors = find_launch_dependencies(sys.argv[1])
    print_errors(errors)
