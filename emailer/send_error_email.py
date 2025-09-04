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

    plain = (
        f"Devxhub Automation TESTING Report by Testing Team\n"
        f"Result: {result_text}\n"
        f"HTTP Status: {http_status}\n"
        f"Time: {now_iso}\n\n"
        f"{message}\n\n"
        f"API Response Body:\n{api_body}\n"
    )

    html = f"""
    <html>
      <body style=\"font-family:Inter,Arial,Helvetica,sans-serif; background:#0b1020; padding:20px;\">
        <div style=\"max-width:820px; margin:auto; background:linear-gradient(180deg,#0f172a,#111827); border:1px solid #1f2937; border-radius:14px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.35);\">
          <div style=\"padding:18px 22px; background:linear-gradient(90deg,#0ea5e9,#8b5cf6); color:#fff;\">
            <h2 style=\"margin:0; letter-spacing:0.2px;\">Devxhub Automation TESTING Report by Testing Team</h2>
            <div style=\"opacity:0.9; font-size:13px;\">{subject}</div>
          </div>
          <div style=\"padding:22px; color:#e5e7eb;\">
            <div style=\"display:flex; gap:12px; margin-bottom:16px;\">
              <div style=\"flex:1; background:#111827; padding:14px; border-radius:10px; text-align:center; border:1px solid #374151;\">
                <div style=\"font-size:12px; color:#9ca3af;\">Result</div>
                <div style=\"font-weight:800; font-size:16px; color:{'#22c55e' if ok else '#f43f5e'};\">{result_text}</div>
              </div>
              <div style=\"flex:1; background:#111827; padding:14px; border-radius:10px; text-align:center; border:1px solid #374151;\">
                <div style=\"font-size:12px; color:#9ca3af;\">HTTP Status</div>
                <div style=\"font-weight:800; font-size:16px;\">{http_status}</div>
              </div>
              <div style=\"flex:1; background:#111827; padding:14px; border-radius:10px; text-align:center; border:1px solid #374151;\">
                <div style=\"font-size:12px; color:#9ca3af;\">Time</div>
                <div style=\"font-weight:800; font-size:14px;\">{now_iso}</div>
              </div>
            </div>

            <p style=\"margin:0 0 14px 0; color:#d1d5db;\">{message}</p>

            <h3 style=\"margin:20px 0 10px 0; color:#a78bfa;\">API Response</h3>
            <pre style=\"white-space:pre-wrap; background:#0b1020; color:#e2e8f0; padding:14px; border-radius:10px; border:1px solid #1f2937;\">{api_body}</pre>

            <p style=\"margin-top:16px; font-size:12px; color:#9ca3af;\">Attachment: enhanced-report.html</p>
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


