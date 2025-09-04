import os
import ssl
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr, formatdate, make_msgid, getaddresses
from typing import List
import re
import json
from datetime import datetime, timezone


def dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for it in items:
        key = it.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def parse_emails(raw_emails: str) -> List[str]:
    parsed = getaddresses([raw_emails or ""])  # returns list of (name, email)
    emails: List[str] = []
    for _name, addr in parsed:
        addr = (addr or '').strip()
        if not addr:
            continue
        # Clean up common wrappers
        addr = addr.strip('<>').strip('"').strip("'")
        # Remove surrounding whitespace
        addr = addr.strip()
        # Basic sanity: must contain single '@' and a dot in domain
        if '@' in addr:
            local, _, domain = addr.partition('@')
            if local and domain and '.' in domain:
                emails.append(addr)
            else:
                print(f"Skipping invalid email address (structure): [masked]")
        else:
            print(f"Skipping invalid email address (no @): [masked]")
    return dedupe_preserve_order(emails)


def read_status(status_path: str = 'artifacts/status.json') -> dict:
    if os.path.exists(status_path):
        try:
            with open(status_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'Failed to read {status_path}: {e}')
    return {"ok": False, "status": "N/A", "body": "No status available"}


def build_email_bodies(subject: str, message: str, status: dict) -> tuple[str, str]:
    ok = status.get('ok')
    http_status = status.get('status')
    api_body = status.get('body')
    now_iso = datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
    result_text = 'SUCCESS' if ok else 'BUG'

    # Color for HTTP status (2xx green, 5xx red, else amber)
    status_str = str(http_status)
    if status_str.startswith('2'):
        status_color = '#22c55e'  # green
    elif status_str.startswith('5'):
        status_color = '#f43f5e'  # red
    else:
        status_color = '#f59e0b'  # amber

    # Static test execution metadata (aligns with the current journey)
    website_url = 'https://devxhub.com/contact-us'
    api_endpoint = 'https://devxhub.com/api/posts/contacts'
    api_method = 'POST'
    test_data = {
        'Name': 'Mejbaur Bahar Fagun',
        'Phone': '+8801316314566',
        'Email': 'fagun.devxhub@gmail.com',
        'Message': 'Automation Testing purpose'
    }

    plain = (
        f"Devxhub Automation TESTING Report by Testing Team\n"
        f"Result: {result_text}\n"
        f"HTTP Status: {http_status}\n"
        f"Time: {now_iso}\n\n"
        f"Summary: {message}\n\n"
        f"Test Execution Details\n"
        f"- Website: {website_url}\n"
        f"- API Endpoint: {api_endpoint}\n"
        f"- Method: {api_method}\n"
        f"- Status Code: {http_status}\n"
        f"- Test Data:\n"
        f"    Name: {test_data['Name']}\n"
        f"    Phone: {test_data['Phone']}\n"
        f"    Email: {test_data['Email']}\n"
        f"    Message: {test_data['Message']}\n\n"
        f"API Response Body:\n{api_body}\n"
    )

    # Mobile-friendly, single title line, fluid layout, wrapped code block + full details
    html = f"""
    <html>
      <body style=\"margin:0; padding:0; background:#0b1020;\">
        <div style=\"box-sizing:border-box; width:100%; padding:12px;\">
          <div style=\"max-width:680px; margin:0 auto; background:linear-gradient(180deg,#0f172a,#111827); border:1px solid #1f2937; border-radius:14px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.35);\">
            <div style=\"padding:16px; background:linear-gradient(90deg,#0ea5e9,#8b5cf6); color:#fff;\">
              <h2 style=\"margin:0; font-family:Inter,Arial,Helvetica,sans-serif; font-size:18px; line-height:1.4; letter-spacing:0.2px;\">Devxhub Automation TESTING Report by Testing Team</h2>
            </div>
            <div style=\"padding:16px; color:#e5e7eb; font-family:Inter,Arial,Helvetica,sans-serif;\">
              <div style=\"display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;\">
                <div style=\"flex:1 1 140px; min-width:140px; background:#111827; padding:12px; border-radius:10px; text-align:center; border:1px solid #374151;\">
                  <div style=\"font-size:12px; color:#9ca3af;\">Result</div>
                  <div style=\"font-weight:800; font-size:16px; color:{'#22c55e' if ok else '#f43f5e'};\">{result_text}</div>
                </div>
                <div style=\"flex:1 1 140px; min-width:140px; background:#111827; padding:12px; border-radius:10px; text-align:center; border:1px solid #374151;\">
                  <div style=\"font-size:12px; color:#9ca3af;\">HTTP Status</div>
                  <div style=\"font-weight:800; font-size:16px; color:{status_color};\">{http_status}</div>
                </div>
                <div style=\"flex:1 1 140px; min-width:140px; background:#111827; padding:12px; border-radius:10px; text-align:center; border:1px solid #374151;\">
                  <div style=\"font-size:12px; color:#9ca3af;\">Time</div>
                  <div style=\"font-weight:800; font-size:12px; word-break:break-word;\">{now_iso}</div>
                </div>
              </div>

              <p style=\"margin:0 0 12px 0; color:#d1d5db; font-size:14px; line-height:1.5;\">{message}</p>

              <h3 style=\"margin:16px 0 8px 0; color:#a78bfa; font-size:14px;\">Test Execution Details</h3>
              <div style=\"background:#111827; border:1px solid #374151; border-radius:10px; padding:12px;\">
                <div style=\"display:flex; gap:8px; margin:6px 0; flex-wrap:wrap;\"><div style=\"min-width:110px; color:#9ca3af; font-size:12px;\">Website</div><div style=\"color:#e5e7eb; font-size:13px;\">{website_url}</div></div>
                <div style=\"display:flex; gap:8px; margin:6px 0; flex-wrap:wrap;\"><div style=\"min-width:110px; color:#9ca3af; font-size:12px;\">API Endpoint</div><div style=\"color:#e5e7eb; font-size:13px;\">{api_endpoint}</div></div>
                <div style=\"display:flex; gap:8px; margin:6px 0; flex-wrap:wrap;\"><div style=\"min-width:110px; color:#9ca3af; font-size:12px;\">Method</div><div style=\"color:#e5e7eb; font-size:13px;\">{api_method}</div></div>
                <div style=\"display:flex; gap:8px; margin:6px 0; flex-wrap:wrap;\"><div style=\"min-width:110px; color:#9ca3af; font-size:12px;\">Status Code</div><div style=\"color:{status_color}; font-size:13px; font-weight:700;\">{http_status}</div></div>
                <div style=\"display:flex; gap:8px; margin:6px 0; flex-wrap:wrap;\"><div style=\"min-width:110px; color:#9ca3af; font-size:12px;\">Test Data</div><div style=\"color:#e5e7eb; font-size:13px;\">Name: {test_data['Name']} • Phone: {test_data['Phone']} • Email: {test_data['Email']} • Message: {test_data['Message']}</div></div>
              </div>

              <h3 style=\"margin:16px 0 8px 0; color:#a78bfa; font-size:14px;\">API Response</h3>
              <div style=\"background:#0b1020; color:#e2e8f0; padding:12px; border-radius:10px; border:1px solid #1f2937; font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size:12px; line-height:1.5; white-space:pre-wrap; word-break:break-word; overflow:auto; max-width:100%;\">{api_body}</div>

              <p style=\"margin-top:14px; font-size:12px; color:#9ca3af;\">Attachments: enhanced-report.html and full HTML report.</p>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    return plain, html


def send_email(subject: str, message: str, attachments: List[str] | None = None) -> None:
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    # Use the authenticated user as the visible From for maximum Gmail compatibility
    email_from = os.getenv('EMAIL_FROM', smtp_user or '') or smtp_user or ''
    email_to = os.getenv('EMAIL_TO', 'fagun115946@gmail.com')

    if not smtp_user or not smtp_pass:
        print('SMTP credentials are not set; skipping email send.')
        return

    # Parse recipients robustly
    email_recipients = parse_emails(email_to)

    print(f'Parsed {len(email_recipients)} recipient(s) from EMAIL_TO')
    print(f'Using SMTP server: {smtp_host}:{smtp_port}')
    print(f'From: {email_from}')
    print(f'Subject: {subject}')
    print(f'Message length: {len(message)} characters')

    if not email_recipients:
        print('No valid recipient emails after parsing; aborting send.')
        return

    # Read status for body enrichment
    status = read_status()

    # Build bodies (plain + html)
    plain_body, html_body = build_email_bodies(subject, message, status)

    # Create outer mixed container
    msg = MIMEMultipart('mixed')

    # Set headers with proper formatting (From must be the authenticated user)
    msg['From'] = formataddr(('Devxhub', email_from))
    msg['To'] = ', '.join(email_recipients)
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid()

    # Create alternative part for plain+html
    alt = MIMEMultipart('alternative')
    alt.attach(MIMEText(plain_body, 'plain', 'utf-8'))
    alt.attach(MIMEText(html_body, 'html', 'utf-8'))
    msg.attach(alt)

    # Attach files if provided
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                filename = os.path.basename(file_path)

                # Create attachment with proper headers
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                part.add_header('Content-Type', f'application/octet-stream; name="{filename}"')

                msg.attach(part)
                print(f'Attached file: {filename} ({len(data)} bytes)')
            except Exception as e:
                print(f'Failed to attach {file_path}: {e}')

    try:
        context = ssl.create_default_context()

        print(f'Connecting to {smtp_host}:{smtp_port}...')

        # Prepare envelope sender/recipients explicitly to avoid header parsing issues
        envelope_from = smtp_user
        envelope_to = email_recipients
        raw_message = msg.as_string()

        # Use SSL for port 465, TLS for other ports
        if smtp_port == 465:
            print('Using SSL connection (port 465)')
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                print('Connected via SSL, attempting login...')
                server.login(smtp_user, smtp_pass)
                print('Login successful, sending email...')
                server.sendmail(envelope_from, envelope_to, raw_message)
                print(f'✅ Email sent successfully to {len(email_recipients)} recipient(s).')
        else:
            print('Using TLS connection (port 587)')
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                print('Connected, starting TLS...')
                server.starttls(context=context)
                print('TLS started, attempting login...')
                server.login(smtp_user, smtp_pass)
                print('Login successful, sending email...')
                server.sendmail(envelope_from, envelope_to, raw_message)
                print(f'✅ Email sent successfully to {len(email_recipients)} recipient(s).')

    except smtplib.SMTPAuthenticationError as e:
        print(f'❌ SMTP Authentication Error: {e}')
        print('Please check your Gmail App Password. Make sure:')
        print('1. 2-Factor Authentication is enabled on your Gmail account')
        print('2. You generated an App Password (not your regular password)')
        print('3. The App Password is correct (16 characters, no spaces)')
    except smtplib.SMTPException as e:
        print(f'❌ SMTP Error: {e}')
        print('This might be due to Gmail\'s strict formatting requirements.')
        print('Try checking the email headers and content format.')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')
        print(f'Error type: {type(e).__name__}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', required=True)
    parser.add_argument('--message', required=True)
    parser.add_argument('--attach', action='append', default=[])
    parser.add_argument('--no-attachments', action='store_true', help='Send email without attachments for testing')
    args = parser.parse_args()

    # If no-attachments flag is set, send without attachments
    attachments = [] if args.no_attachments else args.attach
    send_email(args.subject, args.message, attachments)


if __name__ == '__main__':
    main()


