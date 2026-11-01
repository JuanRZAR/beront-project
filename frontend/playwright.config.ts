import { defineConfig, devices } from "@playwright/test";

const applicationUrl = process.env.BERONT_E2E_BASE_URL;
const temporaryUrl = process.env.BERONT_TEMPORARY_BASE_URL;

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: temporaryUrl
    ? "**/temporary-*.spec.ts"
    : applicationUrl
      ? "**/application*.spec.ts"
      : "**/prototypes.spec.ts",
  outputDir: "./test-results",
  fullyParallel: false,
  reporter: applicationUrl
    ? [
        ["list"],
        ["json", { outputFile: "test-results/application-report.json" }],
      ]
    : "list",
  use: {
    baseURL: temporaryUrl ?? applicationUrl ?? "http://127.0.0.1:4322",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer:
    applicationUrl || temporaryUrl
      ? undefined
      : {
          stdout: "ignore",
          stderr: "ignore",
          command:
            "..\\backend\\.venv\\Scripts\\python.exe -m http.server 4322 --bind 127.0.0.1 --directory ..\\design",
          url: "http://127.0.0.1:4322/prototypes/catalog.html",
          reuseExistingServer: false,
          timeout: 20000,
        },
});
