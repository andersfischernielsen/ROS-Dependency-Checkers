from pprint import pprint

import bashlex
import untangle
import os
import sys
import default_ros_binaries


def setup(path):
    script_pattern = 'grep -rl ' + path + r' -e "#\(\!\)\{0,1\}/bin/bash"'
    packages_pattern = r'find . -type f -name "package.xml"'
    scripts = list(
        map(lambda l: l.strip(), os.popen(script_pattern).readlines()))
    packages_file = os.popen(packages_pattern).readlines()[0].strip()
    parsed = untangle.parse(packages_file)
    run_deps = set(map(lambda e: e.cdata, parsed.package.run_depend))
    all_deps = default_ros_binaries.all_binaries.union(run_deps)
    return (scripts, all_deps)


def validate(scripts, run_deps):
    def dep_exists(s):
        if s and s.kind and s.kind is 'command' and s.parts[0].word not in run_deps:
            return s.parts[0].word
        return None

    def validate_line(line):
        ast = bashlex.parse(line.strip())
        errors = map(lambda a: dep_exists(a), ast)
        filtered = list(filter(lambda e: e is not None, errors))
        if len(filtered) is 0:
            return None
        return list(filtered)

    def validate_script(script):
        with open(script) as f:
            lines = f.readlines()
            if len(lines) > 0 and '/bin/bash' in lines[0]:
                return list(map(lambda l: validate_line(l), lines[1:]))
            return None

    missing = map(lambda s: (s, validate_script(s)), scripts)
    errors = dict(missing)
    return errors


if len(sys.argv) < 2:
    sys.exit('Please run the script with a path to a valid ROS package.')

scripts, run_deps = setup(sys.argv[1])

print('Errors found:')
pprint(validate(scripts, run_deps))
