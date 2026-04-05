// @ts-check
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./",
  testMatch: "*.spec.mjs",
  timeout: 30000,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: process.env.TEST_URL || "https://hopperops.gracezero.ai",
    ignoreHTTPSErrors: true,
  },
});
