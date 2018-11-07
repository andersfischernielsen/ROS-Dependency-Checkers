#!/usr/bin/env python3

import bashlex
import untangle
import os
import sys
import melodic_default


def setup(path):
    script_pattern = 'grep -rl ' + path + r' -e "#\(\!\)\{0,1\}/bin/bash"'
    packages_pattern = r'find . -type f -name "package.xml"'
    scripts = list(
        map(lambda l: l.strip(), os.popen(script_pattern).readlines()))
    packages_file = os.popen(packages_pattern).readlines()[0].strip()
    parsed = untangle.parse(packages_file)
    run_deps = set(map(lambda e: e.cdata, parsed.package.run_depend))
    all_deps = melodic_default.all_binaries.union(run_deps)
    return (scripts, all_deps)


def validate(scripts, run_deps):
    def list_or_none(l):
        if not l:
            return None
        return l

    def dep_exists(s):
        if s and s.kind and s.kind is 'command' and s.parts[0].word not in run_deps:
            return s.parts[0].word
        return None

    def validate_line(line):
        ast = bashlex.parse(line.strip())
        errors = map(lambda a: dep_exists(a), ast)
        filtered = list(filter(lambda e: e is not None, errors))
        return list_or_none(filtered)

    def validate_script(script):
        with open(script) as f:
            lines = f.readlines()
            if lines and '/bin/bash' in lines[0]:
                map_filter = filter(lambda o: o is not None,
                                    map(lambda l: validate_line(l), lines[1:]))
                return list_or_none(list(map_filter))
            return None

    def flatten(llist):
        return [item for sublist in llist for item in sublist]

    missing = dict(map(lambda s: (s, flatten(validate_script(s))), scripts))
    return missing


def print_result(res):
    for (k, v) in res.items():
        print('%s: %s' % (k, ', '.join(v)))


if len(sys.argv) < 2:
    sys.exit('Please run the script with a path to a valid ROS package src.')

scripts, run_deps = setup(sys.argv[1])

print('Missing run_depend(s): ')
res = validate(scripts, run_deps)
print_result(res)
