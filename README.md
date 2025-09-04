# 🚀 Devxhub Website Automation & Monitoring

A Playwright + TypeScript end‑to‑end automation and monitoring suite for the entire `devxhub.com` website. It executes key user journeys on schedule (via GitHub Actions), validates UI/API health, generates modern HTML reports, and sends branded email summaries with the enhanced report attached.

## 📋 Overview

This project is designed to cover multiple critical paths across the site, including but not limited to:
- Landing and navigation checks (global header/footer, key links)
- Contact form submission and API verification
- Services and portfolio discovery paths
- Blog/news visibility and basic SEO signals
- 404/redirect hygiene for legacy links

The suite runs on a schedule (CI) and emails a modern, mobile‑friendly report for rapid triage by the team.

## 🎯 Features

- ✅ Full‑site journey coverage (add journeys incrementally)
- 🧭 Stable navigation with retry logic and robust selectors
- 🔎 UI checks + API response validation where applicable
- 📊 Modern HTML reports (standard + enhanced)
- 📧 Branded email notifications with enhanced report attached
- ⏱️ Scheduled CI runs (GitHub Actions)
- 📱 Mobile‑friendly email content and reports

## 🛠️ Tech Stack

- Playwright Test (TypeScript)
- Node.js (scripts, reporting)
- Python (SMTP email sender)
- GitHub Actions (CI/CD + scheduling)

## 📁 Project Structure

```
Devxhub_Website/
├── tests/
│   ├── devxhub.spec.ts              # Example journey: Contact form + API check
│   └── (add more journeys here)     # e.g., navigation, services, blog
├── emailer/
│   └── send_error_email.py          # SMTP email sender (HTML + plain text)
├── reports/
│   ├── custom-styles.css            # Enhanced report CSS
│   └── generate-enhanced-report.js  # Builds enhanced report
├── playwright-report/               # Generated HTML reports (CI artifact)
├── artifacts/                       # Status JSON written by tests
├── .github/workflows/
│   └── hourly.yml                   # CI workflow (scheduled + manual)
├── playwright.config.ts             # Playwright configuration
├── package.json                     # NPM scripts & deps
└── README.md                        # This file
```

## 🚀 Quick Start (Local)

### Prerequisites
- Node.js 18+
- Python 3.8+
- Git

### Install
```bash
npm install
npx playwright install --with-deps
```

### Run tests
```bash
npm test                 # CLI list reporter
npx playwright test --reporter=html   # generate standard HTML report
```

### Enhanced report (local)
```bash
node reports/generate-enhanced-report.js
# Open: playwright-report/enhanced-report.html
```

## 🧩 Adding New Journeys

1. Create a new file in `tests/`, e.g. `tests/navigation.spec.ts`.
2. Use Playwright Test with clear, resilient selectors.
3. For flows involving backend calls, capture and assert API responses.
4. If a journey indicates site health status, write a concise result snapshot to `artifacts/status.json` (merge or append if you maintain multiple signals).
5. Keep tests independent and fast (aim < 60s each).

Example snippet:
```ts
import { test, expect } from '@playwright/test';

test('Navigation: key links resolve', async ({ page }) => {
  await page.goto('https://devxhub.com');
  await page.getByRole('link', { name: 'Services' }).click();
  await expect(page).toHaveURL(/services/);
});
```

## 🔄 CI/CD (GitHub Actions)

Workflow: `.github/workflows/hourly.yml`
- Schedule: every 8 hours (manual dispatch supported)
- Installs Node, Python, Playwright browsers
- Runs tests, generates reports
- Emails a branded HTML summary with a single attachment:
  - `playwright-report/enhanced-report.html` (falls back to `index.html` if needed)
- Uploads artifacts for download in Actions

## 📧 Email Reporting

- From name: `Devxhub`
- Subject: `Devxhub Automation TESTING Report by Testing Team`
- Body: modern, mobile‑friendly summary (result, HTTP status, timestamp, API response excerpt)
- Attachment: `playwright-report/enhanced-report.html` only

To change branding or recipients, update:
- Email markup: `emailer/send_error_email.py`
- Recipients and SMTP via repo Secrets used in the workflow

## 🐞 Health Signals & Failures

Tests should treat non‑200 API responses or critical UI breakages as failures. The CI email will clearly show SUCCESS/BUG along with HTTP status and context to investigate.

## 🧰 Troubleshooting

- Timeouts: increase in `playwright.config.ts` and verify site availability
- Selector changes: update tests to match current DOM
- SMTP: ensure Gmail App Password and recipients in repo Secrets are correct
- Artifacts: download from the run summary to inspect reports and status JSON

---

This suite is intended to grow iteratively—add new journeys as the site evolves to keep continuous visibility on real user paths across `devxhub.com`.
