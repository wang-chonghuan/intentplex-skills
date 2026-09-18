import { defineConfig } from '@playwright/test';
import { realpathSync } from 'node:fs';
import path from 'node:path';

const runDir = process.env.INTENTGUARD_RUN_DIR;
if (!runDir || !path.isAbsolute(runDir)) {
  throw new Error('Set INTENTGUARD_RUN_DIR to a fresh absolute directory outside the repository.');
}
const relativeRunDir = path.relative(realpathSync(process.cwd()), realpathSync(runDir));
if (relativeRunDir === '' ||
    (!relativeRunDir.startsWith(`..${path.sep}`) && !path.isAbsolute(relativeRunDir))) {
  throw new Error('INTENTGUARD_RUN_DIR must be outside the repository working directory.');
}

export default defineConfig({
  testDir: './tests',
  testMatch: '**/case.spec.?(c|m)[jt]s?(x)',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  forbidOnly: true,
  outputDir: path.join(runDir, 'artifacts'),
  reporter: [
    ['line'],
    ['json', { outputFile: path.join(runDir, 'results.json') }],
  ],
  use: {
    baseURL: process.env.INTENTGUARD_BASE_URL,
    trace: 'retain-on-failure',
  },
  // Derive these static routes and test tags from the approved catalog.
  projects: [
    {
      name: 'chromium',
      grep: /@intentguard:chromium(?:\s|$)/,
      use: { browserName: 'chromium' },
    },
    { name: 'api', grep: /@intentguard:api(?:\s|$)/ },
  ],
});
