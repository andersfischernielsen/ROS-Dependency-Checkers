#!/usr/bin/env python3

import bashlex
import untangle
import os
import re
import sys
import melodic_default


class MissingDependency:
    def __init__(self, dependency, position, line_number=None):
        self.dependency = dependency
        self.position = position
        self.line_number = line_number


def setup(path):
    grep_scripts = 'grep -rl ' + path + r' -e "#\(\!\)\{0,1\}/bin/bash"'
    grep_shebang = 'grep -rl ' + path + \
        r' -e "#\(\!\)\{0,1\}/bin\|usr\|sbin\|bash"'
    packages_pattern = 'find ' + path + r' -type f -name "package.xml"'
    try:
        scripts = list(
            map(lambda l: l.strip(), os.popen(grep_scripts).readlines()))
        shebangs = list(
            map(lambda l: l.strip(), os.popen(grep_shebang).readlines()))

        print(f'Found {len(scripts)} bash scripts.')
        print(f'Found {len(shebangs)} files containing shebangs (#!).')
        packages_file = os.popen(packages_pattern).readlines()[0].strip()
        parsed = untangle.parse(packages_file)

        if not hasattr(parsed, 'package') or (not hasattr(parsed.package, 'run_depend') and not hasattr(parsed.package, 'exec_depend')):
            return (scripts, shebangs, melodic_default)

        run_deps = set()
        exec_deps = set()
        if hasattr(parsed.package, 'run_depend'):
            run_deps = set(map(lambda e: e.cdata, parsed.package.run_depend))
        if hasattr(parsed.package, 'exec_depend'):
            exec_deps = set(map(lambda e: e.cdata, parsed.package.exec_depend))

        all_deps = melodic_default.all_binaries.union(
            run_deps).union(exec_deps)
        return (scripts, shebangs, all_deps)
    except Exception:
        return ([], [], [])


def validate(scripts, shebangs, deps):
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
            if not errors:
                return None
            return (script, errors)

    def validate_shebang(shebang):
        try:
            with open(shebang) as f:
                first = f.readlines()[:1][0].strip()
                regexp = re.compile('(#!)+([/ ][a-z]+)+')
                command = regexp.findall(first)[0]
                command = command[1:][0][1:]
                if command not in deps:
                    return (shebang, [MissingDependency(command, (first.rfind(command), len(first)), 1)])
                return None
        except Exception:
            return None

    def validate_line(line):
        try:
            ast = bashlex.parsesingle(line.strip())
            error = dependency_exists(ast)
            return error
        except Exception:
            return None

    def dependency_exists(ast):
        if not ast or not ast.parts:
            return None

        command = ast.parts[:1][0]
        if command and command.kind is 'word' and command.word not in deps:
            return MissingDependency(command.word, command.pos)
        return None

    bash_missing = dict(
        filter(lambda r: r is not None,
               map(lambda s: validate_script(s), scripts)))

    shebang_missing = dict(
        filter(lambda r: r is not None,
               map(lambda s: validate_shebang(s), shebangs)))

    return (bash_missing, shebang_missing)


def print_result(result):
    if result:
        for script, errors in result.items():
            print('in \'{}\''.format(script))
            if not errors:
                print('    \t\t\t\tNone')
            if (errors):
                for e in errors:
                    print('    ln: {} {} \t\t\t{}'.format(
                        e.line_number, e.position, e.dependency))


if len(sys.argv) < 2:
    sys.exit('Please run the script with a path to a valid ROS package src.')

scripts, shebangs, run_deps = setup(sys.argv[1])
bash_scripts, shebang_scripts = validate(scripts, shebangs, run_deps)
print(f'Found {len(bash_scripts)} possible bash script errors.')
print(f'Found {len(shebang_scripts)} possible shebang (#!) errors.')
print_result(bash_scripts)
print_result(shebang_scripts)
