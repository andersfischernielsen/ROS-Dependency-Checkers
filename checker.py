#!/usr/bin/env python3

import bashlex
import untangle
import os
import sys
import melodic_default


class MissingDependency:
    def __init__(self, dependency, position):
        self.dependency = dependency
        self.position = position
        self.line_number = None


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
    def dependency_exists(ast):
        if not ast or not ast.parts:
            return None

        command = ast.parts[:1][0]
        if command and command.kind is 'word' and command.word not in run_deps:
            return MissingDependency(command.word, command.pos)
        return None

    def validate_line(line):
        ast = bashlex.parsesingle(line.strip())
        error = dependency_exists(ast)
        return error

    def validate_script(script):
        with open(script) as f:
            lines = f.readlines()
            if not lines or not '/bin/bash' in lines[0]:
                return None

            errors = []
            for i, line in enumerate(lines):
                result = validate_line(line)
                if not result:
                    continue
                result.line_number = i
                errors.append(result)
            return errors

    missing = dict(map(lambda s: (s, validate_script(s)), scripts))
    return missing


def print_result(result):
    if res:
        print()
        for script, errors in result.items():
            print('in \'{}\''.format(script))
            for e in errors:
                print('    ln: {} {} \t\t\t{}'.format(
                    e.line_number, e.position, e.dependency))
    else:
        print('None')


if len(sys.argv) < 2:
    sys.exit('Please run the script with a path to a valid ROS package src.')

scripts, run_deps = setup(sys.argv[1])

print('Missing run_depend(s): ')
res = validate(scripts, run_deps)
print_result(res)
