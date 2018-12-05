#!/usr/bin/env node

import { readFileSync } from 'fs';
import parse = require('bash-parser');
import { defaults } from './melodic_default';
import { parse as parseXML } from 'fast-xml-parser';
import { shellSync } from 'execa';

export class MissingDependency {
  dependency: string;
  constructor(dependency: string) {
    this.dependency = dependency;
  }
}

const setup = (path: string) => {
  const grep_scripts = `grep -rl ${path} -e "#\\(\\!\\)\\{0,1\\}/bin/\\(bash\\|sh\\)"`;
  const packages_pattern = `find ${path} -type f -name "package.xml"`;
  const scripts = shellSync(grep_scripts).stdout.split('\n');
  console.log(`Found ${scripts.length} bash scripts.`);
  const packages_files = shellSync(packages_pattern).stdout;
  const xmls = packages_files.split('\n').filter((l) => l !== '');
  let deps = new Set<string>();
  xmls.forEach((x) => {
    const xml = readFileSync(x);
    const parsed = parseXML(xml.toString());
    if (parsed['package']['run_depend']) {
      deps.add(parsed['package']['run_depend']);
    }
    if (parsed['package']['exec_depend']) {
      deps.add(parsed['package']['exec_depend']);
    }
  });
  const all_deps = new Set([...defaults, ...deps]);
  return { scripts, deps: all_deps };
};

const validate = (scripts: string[], deps: Set<string>) => {
  const validate_script = (script: string) => {
    const contents = readFileSync(script).toString();
    try {
      if (
        !contents ||
        (!contents.includes('bin/bash') && !contents.includes('bin/sh'))
      ) {
        return undefined;
      }

      const result = validate(contents);
      return { script, result };
    } catch (e) {
      return undefined;
    }
  };

  const validate = (contents) => {
    try {
      const ast = parse(contents);
      const error = dependency_exists(ast);
      return error;
    } catch (e) {
      return [];
    }
  };

  const dependency_exists = (ast) => {
    if (!ast) {
      return [];
    }

    const commands = ast.commands.filter((c) => c.type && c.type === 'Command');
    const errors: MissingDependency[] = [];
    commands.forEach((c) => {
      if (c.name) {
        const text = c.name.text;
        if (
          text &&
          !deps.has(text) &&
          text !== '/usr/bin/perl' &&
          !text.includes('./') &&
          !text.includes('$')
        ) {
          errors.push(new MissingDependency(text));
        }
      }
    });
    return errors;
  };

  const bash_missing = scripts
    .map((s) => validate_script(s))
    .filter((o) => o && o.result.length);
  return bash_missing;
};

const print_result = (result) => {
  if (result) {
    result.forEach((r) => {
      console.log(`in '${r.script}`);
      if (r.result) {
        r.result.forEach((res) => console.log(`\t\t ${res.dependency}`));
      }
    });
  }
};

if (process.argv.length < 2) {
  console.log('Please run the script with a path to a valid ROS package src.');
  process.exit(1);
}

const scriptsAndDeps = setup(process.argv[2]);
const scripts = scriptsAndDeps.scripts;
const deps = scriptsAndDeps.deps;
const bash_scripts = validate(scripts, deps);
console.log(`Found ${bash_scripts.length} possible bash script errors.`);
print_result(bash_scripts);
