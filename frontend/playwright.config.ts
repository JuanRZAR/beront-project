import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.BERONT_E2E_BASE_URL;
const outputDir = process.env.BERONT_E2E_OUTPUT_DIR || "./test-results";
if (!baseURL)
  throw new Error(
    "Define BERONT_E2E_BASE_URL o ejecuta bun run test:app, que inicia la aplicación.",
  );

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "**/application*.spec.ts",
  outputDir,
  fullyParallel: false,
  workers: 1,
  reporter: [
    ["list"],
    ["json", { outputFile: `${outputDir}/application-report.json` }],
  ],
  use: { baseURL, trace: "retain-on-failure" },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
});
