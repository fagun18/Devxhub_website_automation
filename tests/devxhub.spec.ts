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

async function extractRecaptchaSiteKeyFromHtml(html: string): Promise<string | null> {
  const renderMatch = html.match(/recaptcha\/api\.js\?render=([a-zA-Z0-9_\-]+)/);
  if (renderMatch && renderMatch[1]) {
    return renderMatch[1];
  }
  const dataAttrMatch = html.match(/data-sitekey=\"([^\"]+)\"/);
  if (dataAttrMatch && dataAttrMatch[1]) {
    return dataAttrMatch[1];
  }
  return null;
}

async function obtainRecaptchaToken(page: any): Promise<string | null> {
  // Ensure we're on the contact page so any required cookies/tokens are set
  await gotoWithRetry(page, '/contact-us');
  const html = await page.content();
  const siteKey = await extractRecaptchaSiteKeyFromHtml(html);
  if (!siteKey) {
    return null;
  }

  // Make sure grecaptcha is available; if not, inject via the known script URL
  try {
    await page.addScriptTag({ url: `https://www.google.com/recaptcha/api.js?render=${siteKey}` });
  } catch (_) {
    // Ignore if already present
  }

  try {
    await page.waitForFunction(() => (window as any).grecaptcha && (window as any).grecaptcha.ready, { timeout: 15000 });
    const token = await page.evaluate(async (k: string) => {
      return await new Promise<string>((resolve, reject) => {
        const g: any = (window as any).grecaptcha;
        if (!g || !g.ready) {
          reject(new Error('grecaptcha not ready'));
          return;
        }
        g.ready(() => {
          g.execute(k, { action: 'submit' })
            .then((t: string) => resolve(t))
            .catch((e: any) => reject(e));
        });
      });
    }, siteKey);
    return token;
  } catch (_) {
    return null;
  }
}

test('Devxhub contact API direct call and status check', async ({ page }) => {
  try {
    // Visit site to share cookies/storage with request context and to enable recaptcha
    await gotoWithRetry(page, '/');
    await page.waitForTimeout(1000);
    await gotoWithRetry(page, '/contact-us');

    // Try to obtain a reCAPTCHA v3 token from the page
    const recaptchaToken = await obtainRecaptchaToken(page);

    // Construct payload consistent with production request
    const payload: Record<string, any> = {
      full_name: 'Mejbaur Bahar Fagun',
      email: 'fagun.devxhub@gmail.com',
      phone: '+8801316314566',
      project_details: 'Automation Testing purpose',
    };
    if (recaptchaToken) {
      payload.recaptchaToken = recaptchaToken;
    }

    const response = await page.request.post('https://devxhub.com/api/posts/contacts', {
      data: payload,
      headers: {
        'accept': 'application/json',
        'content-type': 'application/json',
        'origin': 'https://devxhub.com',
        'referer': 'https://devxhub.com/contact-us'
      }
    });

    const status = response.status();
    const bodyText = await response.text();
    let parsed: any = null;
    try {
      parsed = JSON.parse(bodyText);
    } catch (_) {
      parsed = null;
    }

    // Write status file for CI to read
    const outDir = path.join(process.cwd(), 'artifacts');
    fs.mkdirSync(outDir, { recursive: true });
    const statusFile = path.join(outDir, 'status.json');
    const isOk = status === 200;
    const statusPayload: Record<string, any> = {
      ok: isOk,
      status,
      success: parsed?.success ?? isOk,
      message: parsed?.message ?? '',
      body: parsed ? JSON.stringify(parsed, null, 2) : bodyText
    };
    fs.writeFileSync(statusFile, JSON.stringify(statusPayload, null, 2));

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


