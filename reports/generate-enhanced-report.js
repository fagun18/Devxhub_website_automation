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
  
  // Read existing HTML report
  const indexPath = path.join(reportDir, 'index.html');
  let existingHtml = '';
  if (fs.existsSync(indexPath)) {
    existingHtml = fs.readFileSync(indexPath, 'utf8');
  }
  
  const isBug = statusData && !statusData.ok;
  const statusCode = statusData ? statusData.status : 'Unknown';
  const responseBody = statusData ? statusData.body : '';
  
  const enhancedHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Devxhub Contact Form Automation Report</title>
    <link rel="stylesheet" href="custom-styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        .api-details {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .status-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status-badge.success {
            background: rgba(16, 185, 129, 0.1);
            color: #10b981;
        }
        .status-badge.error {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
        }
        .json-viewer {
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
            overflow-x: auto;
            white-space: pre-wrap;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Devxhub Automation Report</h1>
            <div class="subtitle">Contact Form Testing & API Monitoring</div>
        </div>
        
        ${isBug ? `
        <div class="bug-banner">
            🚨 BUG DETECTED: Contact form API returned status ${statusCode}
        </div>
        ` : `
        <div class="success-banner">
            ✅ SUCCESS: Contact form API working correctly
        </div>
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
            <h2 style="margin-bottom: 1.5rem; color: var(--text-primary);">Test Execution Details</h2>
            
            <div class="test-item ${isBug ? 'failed' : 'passed'}">
                <div class="test-header">
                    <h3 class="test-title">Devxhub Contact Form Submission</h3>
                    <span class="test-status ${isBug ? 'failed' : 'passed'}">
                        ${isBug ? 'Failed' : 'Passed'}
                    </span>
                </div>
                <div class="test-details">
                    <div class="detail-row">
                        <div class="detail-label">Website:</div>
                        <div class="detail-value">https://devxhub.com/contact-us</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">API Endpoint:</div>
                        <div class="detail-value">https://devxhub.com/api/posts/contacts</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Method:</div>
                        <div class="detail-value">POST</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Status Code:</div>
                        <div class="detail-value">
                            <span class="status-badge ${isBug ? 'error' : 'success'}">${statusCode}</span>
                        </div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Test Data:</div>
                        <div class="detail-value">
                            Name: Mejbaur Bahar Fagun<br>
                            Phone: +8801316314566<br>
                            Email: fagun.devxhub@gmail.com<br>
                            Message: Automation Testing purpose
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="api-details">
                <h3 style="margin-top: 0; color: var(--text-primary);">API Response Details</h3>
                <div class="json-viewer">${responseBody || 'No response body available'}</div>
            </div>
            
            <div class="api-details">
                <h3 style="margin-top: 0; color: var(--text-primary);">Test Summary</h3>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    ${isBug ? 
                        `The Devxhub contact form automation detected a server error (HTTP ${statusCode}). 
                        This indicates that the contact form API is not functioning properly and requires immediate attention. 
                        The form submission was successful from the frontend perspective, but the backend API returned an error response.` :
                        `The Devxhub contact form automation completed successfully. The API endpoint responded with HTTP 200, 
                        indicating that the contact form is working correctly and submissions are being processed properly.`
                    }
                </p>
            </div>
        </div>
        
        <div class="timestamp">
            Report generated on ${new Date().toLocaleString()} | 
            Devxhub Contact Form Automation v1.0
        </div>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Animate stat cards on load
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.5s ease';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                }, index * 100);
            });
        });
    </script>
</body>
</html>`;

  // Write enhanced report
  fs.writeFileSync(customReportPath, enhancedHtml);
  
  // Copy custom styles to report directory
  const stylesSource = path.join(process.cwd(), 'reports', 'custom-styles.css');
  const stylesDest = path.join(reportDir, 'custom-styles.css');
  if (fs.existsSync(stylesSource)) {
    fs.copyFileSync(stylesSource, stylesDest);
  }
  
  console.log('Enhanced report generated:', customReportPath);
  return customReportPath;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateEnhancedReport();
}

export { generateEnhancedReport };
