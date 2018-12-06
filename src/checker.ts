#!/usr/bin/env node

import { readFileSync } from 'fs';
import parse = require('bash-parser');
import { defaults } from './melodic_default';
import { parse as parseXML } from 'fast-xml-parser';
import { shellSync } from 'execa';

export class MissingDependency {
  dependency: string;
  line: string;
  constructor(c) {
    this.dependency = c.name.text;
    const l = c.suffix ? ' ' + c.suffix.map((s) => s.text).join(' ') : '';
    this.line = l.length <= 40 ? l : `${l.substring(0, 40)}...`;
  }
}

const setup = (path: string) => {
  const grep_scripts = `grep -rl ${path} -e "#\\(\\!\\)\\{0,1\\}/bin/\\(bash\\|sh\\)"`;
  const packages_pattern = `find ${path} -type f -name "package.xml"`;
  try {
    const scripts = shellSync(grep_scripts).stdout.split('\n');
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
  } catch (error) {
    if (error.code !== 1) throw error;
    return { scripts: [], deps: new Set() };
  }
};

const validate = (scripts: string[], deps: Set<string>) => {
  const validate = (contents) => {
    try {
      const ast = parse(contents);
      return dependencyExists(ast);
    } catch (e) {
      return [];
    }
  };

  const dependencyExists = (ast) => {
    if (!ast) return [];
    const commands = ast.commands.filter((c) => c.type && c.type === 'Command');
    const errors: MissingDependency[] = commands.map((c) => {
      if (!c.name || !c.name.text) return undefined;
      const isError =
        c.name.text &&
        !c.name.text.includes('./') &&
        !c.name.text.includes('$') &&
        !deps.has(c.name.text) &&
        !ast.commands.some(
          (f) => f.type === 'Function' && f.name.text === c.name.text,
        );
      if (!isError) return undefined;
      return new MissingDependency(c);
    });
    return errors.filter((e) => e !== undefined);
  };

  const validateScript = (script: string) => {
    const contents = readFileSync(script).toString();
    try {
      if (
        !contents ||
        (!contents.split('\n')[0].includes('bin/bash') &&
          !contents.split('\n')[0].includes('bin/sh'))
      ) {
        return { script, result: undefined };
      }

      const result = validate(contents);
      return { script, result };
    } catch (e) {
      return { script, result: [] };
    }
  };

  const validated = scripts.map((s) => validateScript(s));
  const actualScripts = validated.filter((s) => s.result !== undefined);
  console.log(`Found ${actualScripts.length} bash scripts.`);
  const errors = validated.filter((o) => o && o.result && o.result.length);
  return errors;
};

const print_result = (result) => {
  if (!result) return;
  result.forEach((r) => {
    if (!r.result) return;
    console.log(`in '${r.script}'`);
    r.result.forEach((res) => console.log(`\t\t${res.dependency}`));
  });
};

if (process.argv.length < 2) {
  console.log('Please run the script with a path to a valid ROS package src.');
  process.exit(1);
}

const s = setup(process.argv[2]);
const bash_scripts = validate(s.scripts, s.deps);
console.log(`Found ${bash_scripts.length} possible bash script errors.`);
print_result(bash_scripts);
