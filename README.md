# 🚀 Devxhub Contact Form Automation

A comprehensive Playwright automation project that tests the Devxhub contact form, monitors API responses, and generates beautiful HTML reports with email notifications.

## 📋 Overview

This project automates the testing of the Devxhub contact form (`https://devxhub.com/contact-us`) by:
- Filling out the contact form with predefined test data
- Monitoring the API response from `https://devxhub.com/api/posts/contacts`
- Detecting bugs when the API returns non-200 status codes
- Generating modern, colorful HTML reports
- Sending email notifications on failures
- Running hourly via GitHub Actions

## 🎯 Features

- ✅ **Automated Form Testing**: Fills contact form with test data
- 🚨 **Bug Detection**: Identifies API failures (500 errors, etc.)
- 📊 **Beautiful HTML Reports**: Modern, responsive design with animations
- 📧 **Email Notifications**: Sends alerts on failures with attachments
- ⏰ **Hourly Monitoring**: GitHub Actions runs every hour
- 🔍 **Detailed Logging**: Comprehensive test execution details
- 📱 **Mobile Responsive**: Reports work on all devices

## 🛠️ Tech Stack

- **Playwright**: Browser automation and testing
- **TypeScript**: Type-safe test development
- **Python**: Email notification system
- **GitHub Actions**: CI/CD and scheduling
- **HTML/CSS/JavaScript**: Modern report generation

## 📁 Project Structure

```
Devxhub_Website/
├── tests/
│   └── devxhub.spec.ts          # Main test file
├── emailer/
│   └── send_error_email.py      # Python email sender
├── reports/
│   ├── custom-styles.css        # Report styling
│   └── generate-enhanced-report.js # Report generator
├── playwright-report/           # Generated HTML reports
├── artifacts/                   # Test status files
├── .github/workflows/
│   └── hourly.yml              # GitHub Actions workflow
├── playwright.config.ts        # Playwright configuration
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fagun18/Devxhub_website_automation.git
   cd Devxhub_website_automation
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Install Playwright browsers**
   ```bash
   npx playwright install --with-deps
   ```

### Running Tests

#### Basic Test Run
```bash
npm test
```

#### Test with Enhanced HTML Report
```bash
npm run test:report
```

#### Headed Mode (See browser)
```bash
npm run test:headed
```


## 🔄 GitHub Actions Workflow

The project includes an automated workflow (`.github/workflows/hourly.yml`) that:

1. **Runs every 8 hours** (`0 */8 * * *` cron schedule)
2. **Installs dependencies** (Node.js, Python, Playwright)
3. **Executes tests** with enhanced reporting
4. **Generates HTML reports** and zips them
5. **Sends email notifications** with attachments
6. **Uploads artifacts** for download

### Manual Trigger
You can also trigger the workflow manually:
1. Go to **Actions** tab in GitHub
2. Select **Devxhub Contact Automation**
3. Click **Run workflow**

## 🐛 Bug Detection

The automation detects bugs when:

- **API Status ≠ 200**: Any non-200 HTTP response
- **Network Errors**: Connection failures, timeouts
- **Form Submission Issues**: Element not found, validation errors

## 📈 Monitoring Dashboard

### Success Indicators
- ✅ **Green Status**: API returns 200
- 📧 **Success Email**: "Devxhub contact automation: OK"
- 📊 **Passed Test**: All assertions pass

### Failure Indicators
- ❌ **Red Status**: API returns 500/other errors
- 🚨 **Bug Email**: "BUG: Devxhub contact form not working"
- 📊 **Failed Test**: Assertions fail with error details



## 🚨 Troubleshooting

### Common Issues

1. **Test Timeout**
   - Increase timeout in `playwright.config.ts`
   - Check network connectivity
   - Verify website availability

2. **Form Elements Not Found**
   - Website structure may have changed
   - Update XPath selectors in test file
   - Run in headed mode to debug

3. **GitHub Actions Fails**
   - Check repository secrets
   - Verify workflow file syntax
   - Review action logs for errors

### Debug Mode

Run tests in headed mode to see browser:
```bash
npm run test:headed
```

Check test results:
```bash
# View HTML report
start playwright-report/index.html

# View enhanced report
start playwright-report/enhanced-report.html

# Check status file
cat artifacts/status.json
```
