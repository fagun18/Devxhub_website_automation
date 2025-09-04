import os
import ssl
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr, formatdate, make_msgid
from typing import List
import re


def sanitize_and_validate_emails(raw_emails: str) -> List[str]:
    candidates = []
    for part in re.split(r'[;,]', raw_emails or ''):
        addr = (part or '').strip()
        if not addr:
            continue
        # Remove surrounding angle brackets and quotes
        addr = addr.strip().strip('<>').strip().strip('"').strip("'")
        # Collapse internal spaces
        addr = re.sub(r"\s+", "", addr)
        # Simple RFC5321-safe pattern
        if re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            candidates.append(addr)
        else:
            print(f"Skipping invalid email address: {addr}")
    # De-duplicate preserving order
    seen = set()
    valid = []
    for a in candidates:
        if a.lower() in seen:
            continue
        seen.add(a.lower())
        valid.append(a)
    return valid


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

    # Sanitize and validate recipients
    email_recipients = sanitize_and_validate_emails(email_to)

    print(f"Raw EMAIL_TO: {email_to}")
    print(f'Attempting to send email to: {", ".join(email_recipients) if email_recipients else "<none>"}')
    print(f'Using SMTP server: {smtp_host}:{smtp_port}')
    print(f'From: {email_from}')
    print(f'Subject: {subject}')
    print(f'Message length: {len(message)} characters')

    if not email_recipients:
        print('No valid recipient emails after validation; aborting send.')
        return

    # Create message container with proper encoding
    msg = MIMEMultipart('mixed')

    # Set headers with proper formatting (From must be the authenticated user)
    msg['From'] = formataddr(('Devxhub Automation', email_from))
    msg['To'] = ', '.join(email_recipients)
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid()

    # Add body to email - ensure clean text
    clean_message = message.strip()
    text_part = MIMEText(clean_message, 'plain', 'utf-8')
    msg.attach(text_part)

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
                print(f'✅ Email sent successfully to {len(email_recipients)} recipients: {", ".join(email_recipients)}')
        else:
            print('Using TLS connection (port 587)')
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                print('Connected, starting TLS...')
                server.starttls(context=context)
                print('TLS started, attempting login...')
                server.login(smtp_user, smtp_pass)
                print('Login successful, sending email...')
                server.sendmail(envelope_from, envelope_to, raw_message)
                print(f'✅ Email sent successfully to {len(email_recipients)} recipients: {", ".join(email_recipients)}')

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


