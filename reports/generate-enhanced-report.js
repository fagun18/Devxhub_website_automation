import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function generateEnhancedReport() {
  const reportDir = path.join(process.cwd(), 'playwright-report');
  const artifactsDir = path.join(process.cwd(), 'artifacts');
  const customReportPath = path.join(reportDir, 'enhanced-report.html');
  
  // Read status file if it exists
  let statusData = null;
  const statusFile = path.join(artifactsDir, 'status.json');
  if (fs.existsSync(statusFile)) {
    try {
      statusData = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
    } catch (e) {
      console.log('Could not read status file:', e.message);
    }
  }
  
  // Inline custom CSS (fallback to empty string if missing)
  const customCssPath = path.join(process.cwd(), 'reports', 'custom-styles.css');
  const customCss = fs.existsSync(customCssPath) ? fs.readFileSync(customCssPath, 'utf8') : '';
  
  const isBug = statusData && !statusData.ok;
  const statusCode = statusData ? statusData.status : 'Unknown';
  const responseBody = statusData ? statusData.body : '';
  
  const enhancedHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Devxhub Automation Report</title>
  <style>
    /* Inlined custom styles */
    ${customCss}

    /* Minimal base styles to ensure standalone rendering */
    :root {
      --bg: #0b1020;
      --card: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #475569;
    }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 0; font-family: Inter, Arial, Helvetica, sans-serif; background: var(--bg); }
    .container { max-width: 1100px; margin: 0 auto; padding: 16px; }
    .header { background: #fff; border-radius: 12px; padding: 16px 20px; border: 1px solid #e5e7eb; }
    .header h1 { margin: 0; font-size: 20px; color: var(--text-primary); }
    .subtitle { color: var(--text-secondary); font-size: 13px; margin-top: 4px; }
    .bug-banner, .success-banner { margin: 12px 0; border-radius: 10px; padding: 10px 14px; font-weight: 600; }
    .bug-banner { background: rgba(239,68,68,.1); color: #ef4444; border: 1px solid #fecaca; }
    .success-banner { background: rgba(16,185,129,.1); color: #10b981; border: 1px solid #bbf7d0; }
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .stat-card { background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:14px; text-align:center; }
    .stat-number { font-size:18px; font-weight:800; color:#111827; }
    .stat-label { font-size:12px; color:#6b7280; }
    .test-section { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:16px; margin-top:14px; }
    .test-header { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .test-title { margin:0; font-size:16px; color:#111827; }
    .test-status { font-size:12px; padding:4px 8px; border-radius:999px; border:1px solid #e5e7eb; }
    .test-status.passed { background:#ecfdf5; color:#047857; border-color:#a7f3d0; }
    .test-status.failed { background:#fef2f2; color:#b91c1c; border-color:#fecaca; }
    .detail-row { display:flex; gap:8px; margin:6px 0; }
    .detail-label { min-width:120px; color:#475569; font-size:13px; }
    .detail-value { color:#0f172a; font-size:13px; }
    .api-details { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:14px; margin:12px 0; }
    .json-viewer { background:#0b1020; color:#e2e8f0; padding:12px; border-radius:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size:12px; line-height:1.5; white-space:pre-wrap; word-break:break-word; overflow:auto; max-width:100%; }
    .timestamp { color:#94a3b8; font-size:12px; margin:12px 2px; }

    /* Responsive */
    @media (max-width: 768px) {
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .detail-row { flex-direction: column; }
      .detail-label { min-width: unset; }
      .container { padding: 12px; }
    }
    @media (max-width: 420px) {
      .stats-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Devxhub Automation Report</h1>
      <div class="subtitle">Contact Form Testing & API Monitoring</div>
    </div>

    ${isBug ? `
    <div class="bug-banner">🚨 BUG DETECTED: Contact form API returned status ${statusCode}</div>
    ` : `
    <div class="success-banner">✅ SUCCESS: Contact form API working correctly</div>
    `}

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number ${isBug ? 'failed' : 'passed'}">${isBug ? '❌' : '✅'}</div>
        <div class="stat-label">API Status</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${statusCode}</div>
        <div class="stat-label">HTTP Code</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${new Date().toLocaleTimeString()}</div>
        <div class="stat-label">Test Time</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${isBug ? 'BUG' : 'OK'}</div>
        <div class="stat-label">Result</div>
      </div>
    </div>

    <div class="test-section">
      <div class="test-header">
        <h3 class="test-title">Devxhub Contact Form Submission</h3>
        <span class="test-status ${isBug ? 'failed' : 'passed'}">${isBug ? 'Failed' : 'Passed'}</span>
      </div>

      <div class="detail-row"><div class="detail-label">Website:</div><div class="detail-value">https://devxhub.com/contact-us</div></div>
      <div class="detail-row"><div class="detail-label">API Endpoint:</div><div class="detail-value">https://devxhub.com/api/posts/contacts</div></div>
      <div class="detail-row"><div class="detail-label">Method:</div><div class="detail-value">POST</div></div>
      <div class="detail-row"><div class="detail-label">Status Code:</div><div class="detail-value"><span class="test-status ${isBug ? 'failed' : 'passed'}">${statusCode}</span></div></div>
      <div class="detail-row"><div class="detail-label">Test Data:</div><div class="detail-value">Name: Mejbaur Bahar Fagun<br>Phone: +8801316314566<br>Email: fagun.devxhub@gmail.com<br>Message: Automation Testing purpose</div></div>

      <div class="api-details">
        <h3 style="margin-top:0; color:#0f172a;">API Response Details</h3>
        <div class="json-viewer">${responseBody || 'No response body available'}</div>
      </div>

      <div class="api-details">
        <h3 style="margin-top:0; color:#0f172a;">Test Summary</h3>
        <p style="color:#475569; line-height:1.6;">
          ${isBug ? `The Devxhub contact form automation detected a server error (HTTP ${statusCode}). The form submission was successful from the frontend perspective, but the backend API returned an error response.` : `The Devxhub contact form automation completed successfully. The API endpoint responded with HTTP 200, indicating that the contact form is working correctly and submissions are being processed properly.`}
        </p>
      </div>
    </div>

    <div class="timestamp">Report generated on ${new Date().toLocaleString()} | Devxhub Contact Form Automation v1.0</div>
  </div>
</body>
</html>`;

  // Write enhanced report
  fs.writeFileSync(customReportPath, enhancedHtml);

  console.log('Enhanced report generated:', customReportPath);
  return customReportPath;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateEnhancedReport();
}

export { generateEnhancedReport };
