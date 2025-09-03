import { test, expect } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

async function sendErrorEmail(subject: string, message: string): Promise<void> {
  const result = spawnSync('python', [
    'emailer/send_error_email.py',
    '--subject', subject,
    '--message', message
  ], { stdio: 'inherit' });
  if (result.error) {
    // As a fallback, attempt python3
    spawnSync('python3', [
      'emailer/send_error_email.py',
      '--subject', subject,
      '--message', message
    ], { stdio: 'inherit' });
  }
}

async function gotoWithRetry(page: any, url: string, tries = 3): Promise<void> {
  let lastError: any = null;
  for (let attempt = 1; attempt <= tries; attempt++) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      return;
    } catch (e) {
      lastError = e;
      if (attempt < tries) {
        await page.waitForTimeout(2000);
        continue;
      }
    }
  }
  throw lastError;
}

test('Devxhub contact form submission and API status check', async ({ page }) => {
  try {
    await gotoWithRetry(page, '/');
    await page.waitForTimeout(2000);

    await gotoWithRetry(page, '/contact-us');
    await page.waitForSelector('xpath=/html/body//form//button', { timeout: 60000 }).catch(() => {});

    const fullName = page.locator('xpath=/html/body/div[1]/div/div[2]/div/section/div[1]/div/div/div[2]/form/div[1]/input');
    await fullName.click();
    await fullName.fill('Mejbaur Bahar Fagun');

    const phone = page.locator('xpath=/html/body/div[1]/div/div[2]/div/section/div[1]/div/div/div[2]/form/div[2]/div[1]/div/div/input');
    await phone.click();
    await phone.fill('+8801316314566');

    const email = page.locator('xpath=/html/body/div[1]/div/div[2]/div/section/div[1]/div/div/div[2]/form/div[2]/div[2]/input');
    await email.click();
    await email.fill('fagun.devxhub@gmail.com');

    const details = page.locator('xpath=/html/body/div[1]/div/div[2]/div/section/div[1]/div/div/div[2]/form/div[3]/textarea');
    await details.click();
    await details.fill('Automation Testing purpose');

    const responsePromise = page.waitForResponse((resp) => {
      return resp.url() === 'https://devxhub.com/api/posts/contacts' && resp.request().method() === 'POST';
    }, { timeout: 30000 });

    const submit = page.locator('xpath=/html/body/div[1]/div/div[2]/div/section/div[1]/div/div/div[2]/form/button');
    await submit.click();

    const response = await responsePromise;
    const status = response.status();
    const bodyText = await response.text();

    // Write status file for CI to read
    const outDir = path.join(process.cwd(), 'artifacts');
    fs.mkdirSync(outDir, { recursive: true });
    const statusFile = path.join(outDir, 'status.json');
    const isOk = status === 200;
    fs.writeFileSync(statusFile, JSON.stringify({ ok: isOk, status, body: bodyText }, null, 2));

    if (!isOk) {
      await sendErrorEmail(
        `BUG: Devxhub contact form not working (status ${status})`,
        `BUG detected on contact form. Endpoint responded with status ${status}.\nResponse:\n${bodyText}`
      );
      // Also assert fail to make test red
      expect(status, 'Contact form API must return 200').toBe(200);
    }
  } catch (error: any) {
    await sendErrorEmail(
      'BUG: Devxhub contact automation failed',
      `BUG detected: Automation encountered an error: ${error?.message || String(error)}`
    );
    // Ensure failure bubbles to test report
    throw error;
  }
});


