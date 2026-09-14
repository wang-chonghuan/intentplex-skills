#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { readFileSync, realpathSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const commands = {
  list: [0, 0, {}],
  info: [1, 1, { '--detail': 'boolean' }],
  doc: [1, 1, {}],
  demo: [1, 2, {}],
  token: [0, 1, {}],
  semantic: [1, 1, {}],
  'design.md': [0, 0, {}],
  changelog: [0, 3, {}],
  doctor: [0, 0, {}],
  env: [0, 1, {}],
  usage: [0, 1, { '--filter': 'value' }],
  lint: [0, 1, {
    '--only': 'value',
    '--antd-alias': 'value',
    '--diff': 'optional',
    '--staged': 'boolean',
  }],
  migrate: [2, 2, { '--component': 'value' }],
};

class ToolError extends Error {
  constructor(code, message, details) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

function fail(code, message, details) {
  throw new ToolError(code, message, details);
}

export function parseRequest(argv, cwd = process.cwd()) {
  const args = [...argv];
  let project = cwd;
  if (args[0] === '--project') {
    args.shift();
    project = args.shift();
    if (!project || project.startsWith('-')) {
      fail('ARGUMENT', '--project requires a frontend package directory.');
    }
  }
  const command = args.shift();
  if (!Object.hasOwn(commands, command)) {
    fail('ARGUMENT', `Use a read-only command: ${Object.keys(commands).join(', ')}.`);
  }
  const [min, max, specific] = commands[command];
  const options = { '--lang': 'value', ...specific };
  let positionalCount = 0;
  const seen = new Set();
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (!arg.startsWith('-')) {
      positionalCount += 1;
      continue;
    }
    if (!Object.hasOwn(options, arg)) {
      fail('ARGUMENT', `Unsupported option ${arg}; version and JSON format are managed by this helper.`);
    }
    if (seen.has(arg) && arg !== '--antd-alias') {
      fail('ARGUMENT', `Duplicate option: ${arg}.`);
    }
    seen.add(arg);
    const kind = options[arg];
    const next = args[index + 1];
    if (kind === 'value' && (!next || next.startsWith('-'))) {
      fail('ARGUMENT', `${arg} requires a value.`);
    }
    if (kind === 'value' || (kind === 'optional' && next && !next.startsWith('-'))) {
      index += 1;
    }
  }
  if (positionalCount < min || positionalCount > max) {
    fail('ARGUMENT', `${command} expects ${min === max ? min : `${min}-${max}`} positional argument(s).`);
  }
  if (seen.has('--diff') && seen.has('--staged')) {
    fail('ARGUMENT', 'Choose either --diff or --staged.');
  }
  return { project: resolve(cwd, project), command, args };
}

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail('LOCAL_PACKAGE', `Cannot read valid JSON at ${path}.`, error.message);
  }
}

function localPackage(project, manifest, name) {
  const resolver = createRequire(join(project, 'package.json'));
  let manifestPath;
  try {
    manifestPath = resolver.resolve(`${name}/package.json`);
  } catch {
    fail('LOCAL_PACKAGE', `${name} must be locally installed. No global or network fallback is performed.`);
  }
  const metadata = readJson(manifestPath);
  const pins = [manifest.dependencies?.[name], manifest.devDependencies?.[name]]
    .filter((value) => value !== undefined);
  const exactVersion = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
  if (metadata?.name !== name || !exactVersion.test(metadata.version ?? '')) {
    fail('LOCAL_PACKAGE', `Invalid installed metadata for ${name}.`);
  }
  if (!pins.length || pins.some((pin) => pin !== metadata.version)) {
    fail('VERSION_PIN', `Pin ${name} exactly to its verified installed release (${metadata.version}) in this frontend package before using the helper. Do not change versions without authorization.`);
  }
  return { metadata, root: dirname(manifestPath) };
}

export function validateLintReport(data) {
  const failures = [];
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return { pass: false, failures: ['Expected a lint report object.'] };
  }
  if (Object.keys(data).some((key) => !['issues', 'skippedFiles', 'partial', 'summary'].includes(key))) {
    failures.push('Unknown lint report fields; review the CLI schema before adapting this validator.');
  }
  if (data.error) failures.push('CLI reported an error.');
  if (!Array.isArray(data.issues)) failures.push('Missing issues array.');
  if (!Array.isArray(data.skippedFiles)) failures.push('Missing skippedFiles array.');
  if (data.partial !== false) failures.push('Scan is partial or its completeness is unknown.');
  const summary = data.summary;
  const counts = ['total', 'deprecated', 'a11y', 'usage', 'performance', 'skipped'];
  if (!summary || typeof summary !== 'object' || Array.isArray(summary)
    || counts.some((key) => !Number.isSafeInteger(summary[key]) || summary[key] < 0)) {
    failures.push('Missing or invalid lint summary; review the CLI schema before adapting this validator.');
  } else {
    if (Object.keys(summary).some((key) => !counts.includes(key))) {
      failures.push('Unknown lint summary fields; review the CLI schema before adapting this validator.');
    }
    if (summary.total !== data.issues?.length) failures.push('Issue count does not match the summary.');
    if (summary.skipped !== data.skippedFiles?.length) failures.push('Skipped count does not match the summary.');
    if (summary.total !== summary.deprecated + summary.a11y + summary.usage + summary.performance) {
      failures.push('Lint category totals are inconsistent.');
    }
    if (counts.some((key) => summary[key] !== 0)) failures.push('Lint summary contains findings or skips.');
  }
  if (data.issues?.length) failures.push('Lint findings must be resolved, including warnings.');
  if (data.skippedFiles?.length) failures.push('Skipped files cannot count as a complete scan.');
  return { pass: failures.length === 0, failures };
}

export function execute(argv) {
  const request = parseRequest(argv);
  const manifest = readJson(join(request.project, 'package.json'));
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) {
    fail('LOCAL_PACKAGE', 'The frontend package manifest must be an object.');
  }
  const ant = localPackage(request.project, manifest, 'antd');
  const cli = localPackage(request.project, manifest, '@ant-design/cli');
  const bin = typeof cli.metadata.bin === 'string' ? cli.metadata.bin : cli.metadata.bin?.antd;
  if (typeof bin !== 'string' || !bin) fail('LOCAL_PACKAGE', 'The local Ant CLI has no antd executable.');
  const entry = resolve(cli.root, bin);
  const local = relative(cli.root, entry);
  if (isAbsolute(local) || local === '..' || local.startsWith(`..${process.platform === 'win32' ? '\\' : '/'}`)) {
    fail('LOCAL_PACKAGE', 'The CLI executable must be inside its installed package.');
  }
  const args = [entry, request.command, ...request.args, '--version', ant.metadata.version, '--format', 'json'];
  const result = spawnSync(process.execPath, args, {
    cwd: request.project,
    encoding: 'utf8',
    timeout: 120_000,
    maxBuffer: 32 * 1024 * 1024,
    windowsHide: true,
    env: { ...process.env, NO_UPDATE_CHECK: '1', ANTD_NO_AUTO_REPORT: '1' },
  });
  if (result.error || result.status !== 0) {
    fail('CLI_FAILED', 'The local Ant CLI did not finish successfully.', {
      exitCode: result.status,
      signal: result.signal,
      error: result.error?.message,
      stdout: result.stdout,
      stderr: result.stderr,
    });
  }
  let data;
  try {
    data = JSON.parse(result.stdout);
  } catch {
    fail('CLI_SCHEMA', 'The CLI did not return valid JSON.', { stdout: result.stdout, stderr: result.stderr });
  }
  if (!data || typeof data !== 'object' || data.error) {
    fail('CLI_SCHEMA', 'Expected structured successful CLI data.', data);
  }
  const envelope = {
    project: request.project,
    command: request.command,
    arguments: request.args,
    versions: { antd: ant.metadata.version, cli: cli.metadata.version },
    data,
    ...(result.stderr ? { diagnostics: result.stderr } : {}),
    ...(request.command === 'lint' ? { reportValidation: validateLintReport(data) } : {}),
  };
  return { envelope, exitCode: envelope.reportValidation?.pass === false ? 1 : 0 };
}

function main() {
  try {
    const result = execute(process.argv.slice(2));
    process.stdout.write(`${JSON.stringify(result.envelope, null, 2)}\n`);
    process.exitCode = result.exitCode;
  } catch (error) {
    process.stderr.write(`${JSON.stringify({
      error: true,
      code: error.code ?? 'INTERNAL',
      message: error.message,
      ...(error.details !== undefined ? { details: error.details } : {}),
    }, null, 2)}\n`);
    process.exitCode = 2;
  }
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) main();
