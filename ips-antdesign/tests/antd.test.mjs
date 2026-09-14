import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { parseRequest, validateLintReport } from '../scripts/antd.mjs';

const script = fileURLToPath(new URL('../scripts/antd.mjs', import.meta.url));
const cleanReport = () => ({
  issues: [],
  skippedFiles: [],
  partial: false,
  summary: { total: 0, deprecated: 0, a11y: 0, usage: 0, performance: 0, skipped: 0 },
});

function fixture(t, { report = cleanReport(), status = 0, raw, pins = {} } = {}) {
  const project = mkdtempSync(join(tmpdir(), 'ips-antdesign-test-'));
  t.after(() => rmSync(project, { recursive: true, force: true }));
  const manifest = {
    name: 'test-app',
    dependencies: { antd: pins.antd ?? '6.0.0' },
    devDependencies: { '@ant-design/cli': pins.cli ?? '6.0.0' },
  };
  const put = (path, value) => {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, typeof value === 'string' ? value : JSON.stringify(value));
  };
  put(join(project, 'package.json'), manifest);
  put(join(project, 'node_modules/antd/package.json'), { name: 'antd', version: '6.0.0' });
  put(join(project, 'node_modules/@ant-design/cli/package.json'), {
    name: '@ant-design/cli', version: '6.0.0', bin: { antd: 'cli.cjs' },
  });
  const output = raw === undefined ? JSON.stringify(report) : raw;
  put(join(project, 'node_modules/@ant-design/cli/cli.cjs'), `
const fs = require('node:fs');
fs.writeFileSync('invocation.json', JSON.stringify({
  args: process.argv.slice(2),
  noUpdate: process.env.NO_UPDATE_CHECK,
  noReport: process.env.ANTD_NO_AUTO_REPORT
}));
process.stdout.write(${JSON.stringify(output)});
process.exitCode = ${status};
`);
  const run = (args, entry = script) => spawnSync(process.execPath, [entry, ...args], {
    cwd: project, encoding: 'utf8', timeout: 10_000,
  });
  return { project, run, put };
}

test('allows a local query and resolves the explicit project', () => {
  assert.deepEqual(parseRequest(['--project', 'frontend', 'info', 'Table', '--detail'], '/tmp'), {
    project: resolve('/tmp/frontend'), command: 'info', args: ['Table', '--detail'],
  });
});

test('read-only commands and required positional arguments are enforced', () => {
  for (const args of [[], ['upgrade'], ['setup'], ['bug', '--submit'], ['constructor'], ['info'], ['list', 'Button']]) {
    assert.throws(() => parseRequest(args), /read-only|expects/);
  }
});

test('rejects overriding versions, output, project or applying a migration', () => {
  for (const args of [
    ['info', 'Table', '--version', '5.0.0'],
    ['info', 'Table', '--version=5.0.0'],
    ['info', 'Table', '--format', 'text'],
    ['info', 'Table', '-V'],
    ['info', 'Table', '--project', '/tmp/elsewhere'],
    ['migrate', '5', '6', '--apply', './src'],
    ['migrate', '5', '6', '--confirm'],
  ]) assert.throws(() => parseRequest(args), /Unsupported option/);
});

test('validates options and supports repeated aliases without shell parsing', () => {
  for (const args of [
    ['--project'],
    ['--project', '--bad', 'info', 'Button'],
    ['doc', 'Table', '--lang'],
    ['doc', 'Table', '--lang', 'zh', '--lang', 'en'],
    ['lint', './src', '--staged', '--diff'],
  ]) assert.throws(() => parseRequest(args), /requires|Duplicate|Choose/);
  assert.equal(parseRequest(['lint', './src', '--antd-alias', '@ui', '--antd-alias', '@shared']).command, 'lint');
  assert.equal(parseRequest(['lint', './src', '--diff', 'main']).command, 'lint');
});

test('a complete clean lint report passes', () => {
  assert.deepEqual(validateLintReport(cleanReport()), { pass: true, failures: [] });
});

test('malformed or unknown lint schema fails closed', () => {
  for (const data of [null, [], '', {}, { ...cleanReport(), summary: null }, { ...cleanReport(), partial: undefined }]) {
    assert.equal(validateLintReport(data).pass, false);
  }
});

test('warnings fail even when the process would succeed', () => {
  const report = cleanReport();
  report.issues.push({ file: 'test.tsx', severity: 'warning', rule: 'usage', message: 'Use App context.' });
  report.summary.total = 1;
  report.summary.usage = 1;
  assert.equal(validateLintReport(report).pass, false);
});

test('skipped or partial scans fail', () => {
  const report = cleanReport();
  report.skippedFiles.push({ file: 'bad.tsx', reason: 'parse-error' });
  report.summary.skipped = 1;
  assert.equal(validateLintReport(report).pass, false);
  assert.equal(validateLintReport({ ...cleanReport(), partial: true }).pass, false);
});

test('inconsistent, nonnumeric or negative summaries fail', () => {
  for (const summary of [
    { ...cleanReport().summary, total: 1 },
    { ...cleanReport().summary, usage: 1 },
    { ...cleanReport().summary, total: '0' },
    { ...cleanReport().summary, skipped: -1 },
    { ...cleanReport().summary, performance: 0.5 },
  ]) assert.equal(validateLintReport({ ...cleanReport(), summary }).pass, false);
});

test('new report or summary fields require schema review rather than silent acceptance', () => {
  assert.equal(validateLintReport({ ...cleanReport(), parseErrors: ['bad input'] }).pass, false);
  assert.equal(validateLintReport({
    ...cleanReport(), summary: { ...cleanReport().summary, fatal: 1 },
  }).pass, false);
});

test('uses the local pin, JSON output, and opt-out environment', (t) => {
  const { project, run } = fixture(t, { report: { name: 'Table', props: [] } });
  const result = run(['info', 'Table']);
  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.deepEqual(output.versions, { antd: '6.0.0', cli: '6.0.0' });
  assert.equal(output.reportValidation, undefined);
  const call = JSON.parse(readFileSync(join(project, 'invocation.json'), 'utf8'));
  assert.deepEqual(call.args, ['info', 'Table', '--version', '6.0.0', '--format', 'json']);
  assert.equal(call.noUpdate, '1');
  assert.equal(call.noReport, '1');
});

test('clean lint gets a report-integrity pass, not an adoption verdict', (t) => {
  const { run } = fixture(t);
  const result = run(['lint', './src']);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).reportValidation.pass, true);
  assert.equal(JSON.parse(result.stdout).migrationComplete, undefined);
});

test('zero-exit lint with findings returns nonzero and retains evidence', (t) => {
  const report = cleanReport();
  report.issues = [{ severity: 'warning', rule: 'usage', message: 'Violation' }];
  report.summary.total = report.summary.usage = 1;
  const { run } = fixture(t, { report });
  const result = run(['lint', './src']);
  assert.equal(result.status, 1);
  const output = JSON.parse(result.stdout);
  assert.equal(output.data.issues.length, 1);
  assert.equal(output.reportValidation.pass, false);
});

test('zero-exit lint with a missing completeness field returns nonzero', (t) => {
  const report = cleanReport();
  delete report.partial;
  const { run } = fixture(t, { report });
  assert.equal(run(['lint', './src']).status, 1);
});

test('a CLI process failure is not accepted even with clean JSON', (t) => {
  const { run } = fixture(t, { status: 7 });
  const result = run(['lint', './src']);
  assert.equal(result.status, 2);
  const error = JSON.parse(result.stderr);
  assert.equal(error.code, 'CLI_FAILED');
  assert.equal(error.details.exitCode, 7);
});

test('invalid JSON output fails, without being treated as an empty report', (t) => {
  const { run } = fixture(t, { raw: 'Update available\n{}' });
  const result = run(['lint', './src']);
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stderr).code, 'CLI_SCHEMA');
});

test('a structured CLI error fails even if exit code is zero', (t) => {
  const { run } = fixture(t, { report: { error: true, message: 'Unknown component' } });
  const result = run(['info', 'Bubble']);
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stderr).code, 'CLI_SCHEMA');
});

test('a range or mismatched installed version is rejected without invoking CLI', (t) => {
  for (const pins of [{ antd: '^6.0.0' }, { cli: '6.0.1' }]) {
    const { project, run } = fixture(t, { pins });
    const result = run(['info', 'Button']);
    assert.equal(result.status, 2);
    assert.equal(JSON.parse(result.stderr).code, 'VERSION_PIN');
    assert.throws(() => readFileSync(join(project, 'invocation.json')), /ENOENT/);
  }
});

test('missing local CLI does not install or fall back globally', (t) => {
  const { project, run } = fixture(t);
  rmSync(join(project, 'node_modules/@ant-design/cli'), { recursive: true });
  const result = run(['info', 'Button']);
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stderr).code, 'LOCAL_PACKAGE');
});

test('unsafe commands cannot execute or mutate the project', (t) => {
  const { project, run } = fixture(t);
  const before = readFileSync(join(project, 'package.json'), 'utf8');
  const result = run(['setup', '--client', 'codex']);
  assert.equal(result.status, 2);
  assert.equal(readFileSync(join(project, 'package.json'), 'utf8'), before);
  assert.throws(() => readFileSync(join(project, 'invocation.json')), /ENOENT/);
});

test('works when the skill is exposed through a directory symlink', (t) => {
  const { project, run } = fixture(t);
  const linked = join(project, 'linked-skill');
  symlinkSync(dirname(dirname(script)), linked, 'dir');
  const result = run(['lint', './src'], join(linked, 'scripts/antd.mjs'));
  assert.equal(result.status, 0, result.stderr);
});

test('rejects an executable escaping its package', (t) => {
  const { project, run, put } = fixture(t);
  put(join(project, 'node_modules/@ant-design/cli/package.json'), {
    name: '@ant-design/cli', version: '6.0.0', bin: { antd: '../other.cjs' },
  });
  const result = run(['info', 'Table']);
  assert.equal(result.status, 2);
  assert.match(JSON.parse(result.stderr).message, /inside its installed package/);
});
