#!/usr/bin/env node

import { readFileSync } from 'fs';
import parse = require('bash-parser');
import { defaults } from './melodic_default';
import { parse as parseXML } from 'fast-xml-parser';
import { shellSync } from 'execa';

type Name = { text: string; type: string };
type Command = { type: string; name: Name; suffix: Name[] };
type AST = { type: string; commands: Command[] };
type Error = 'Error';
type MissingDependency = Dependency | Error;
type Result = { script: string; result: MissingDependency[] | Error };

class Dependency {
  dependency: string;
  line: string;
  constructor(c: Command) {
    this.dependency = c.name.text;
    const l = c.suffix ? c.suffix.reduce((i, n) => `${i} ${n.text}`, '') : '';
    this.line = l.length <= 40 ? l : `${l.substring(0, 40)}...`;
  }
}

const getDependencies = (path: string) => {
  const getDependency = (x: string) => {
    const xml = readFileSync(x);
    const parsed: string = parseXML(xml.toString());
    if (parsed['package']['run_depend']) {
      return parsed['package']['run_depend'];
    }
    if (parsed['package']['exec_depend']) {
      return parsed['package']['exec_depend'];
    }
    return '';
  };

  const grepForScripts = `grep -rl --exclude=".travis.sh" --exclude-dir={.git,.travis} ${path} -e "#\\(\\!\\)\\{0,1\\}/bin/\\(bash\\|sh\\)"`;
  const packagesPattern = `find ${path} -type f -name "package.xml"`;
  try {
    const scripts = shellSync(grepForScripts).stdout.split('\n');
    const packageFiles = shellSync(packagesPattern).stdout;
    const xmls = packageFiles.split('\n').filter((l) => l !== '');
    const allDependencies = xmls.map(getDependency).filter((d) => d !== '');
    let dependencies = new Set<string>(allDependencies);
    const all_dependencies = new Set([...defaults, ...dependencies]);
    return { scripts, dependencies: all_dependencies };
  } catch (error) {
    if (error.code !== 1) throw error;
    return { scripts: [] as string[], dependencies: new Set() };
  }
};

const validate = (scripts: string[], dependencies: Set<string>) => {
  const validate = (contents: string) => {
    try {
      const ast = parse(contents);
      return dependencyExists(ast);
    } catch (e) {
      return [];
    }
  };

  const dependencyExists = (ast: AST) => {
    if (!ast) return [];
    const commands: Command[] = ast.commands.filter(
      (c: Command) => c.type && c.type === 'Command',
    );
    const errors: MissingDependency[] = commands.map((c) => {
      if (!c.name || !c.name.text) return 'Error';
      const isError =
        c.name.text &&
        !c.name.text.includes('./') &&
        !c.name.text.includes('$') &&
        !dependencies.has(c.name.text) &&
        !ast.commands.some(
          (f: Command) => f.type === 'Function' && f.name.text === c.name.text,
        );
      if (!isError) return 'Error';
      return new Dependency(c);
    });
    return errors.filter((e) => e !== 'Error');
  };

  const validateScript = (script: string): Result => {
    const contents = readFileSync(script).toString();
    try {
      if (
        !contents ||
        (!contents.split('\n')[0].includes('bin/bash') &&
          !contents.split('\n')[0].includes('bin/sh'))
      ) {
        return { script, result: 'Error' };
      }

      const result = validate(contents);
      return { script, result };
    } catch (e) {
      return { script, result: [] };
    }
  };

  const validated = scripts.map((s) => validateScript(s));
  const actualScripts = validated.filter((s) => s.result !== 'Error');
  console.log(`Found ${actualScripts.length} bash scripts.`);
  const errors = validated.filter((o) => o && o.result && o.result.length);
  return errors;
};

const printResult = (result: Result[]) => {
  if (!result) return;
  result.forEach((r) => {
    if (r.result === 'Error') return;
    console.log(`in '${r.script}'`);
    r.result.forEach((res) => {
      if (res === 'Error') return;
      console.log(`\t\t${res.dependency}`);
    });
  });
};

if (process.argv.length < 2) {
  console.log('Please supply a path to a valid ROS package src.');
  process.exit(1);
}

const s = getDependencies(process.argv[2]);
const validated = validate(s.scripts, s.dependencies);
if (validated.length <= 1) console.log(`Found 1 possible bash script error.`);
else console.log(`Found ${validated.length} possible bash script errors.`);
printResult(validated);
