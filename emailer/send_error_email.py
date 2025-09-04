import os
import ssl
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List


def send_email(subject: str, message: str, attachments: List[str] | None = None) -> None:
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    email_from = os.getenv('EMAIL_FROM', smtp_user or '')
    email_to = os.getenv('EMAIL_TO', 'fagun115946@gmail.com')

    if not smtp_user or not smtp_pass:
        print('SMTP credentials are not set; skipping email send.')
        return

    # Parse multiple email addresses (comma-separated)
    email_recipients = [email.strip() for email in email_to.split(',') if email.strip()]

    print(f'Attempting to send email to: {", ".join(email_recipients)}')
    print(f'Using SMTP server: {smtp_host}:{smtp_port}')
    print(f'From: {email_from}')
    print(f'Subject: {subject}')
    print(f'Message length: {len(message)} characters')

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = ', '.join(email_recipients)
    msg['Subject'] = subject

    # Add body to email - ensure clean text
    clean_message = message.strip()
    msg.attach(MIMEText(clean_message, 'plain', 'utf-8'))

    # Attach files if provided
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                filename = os.path.basename(file_path)
                
                # Create attachment
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                
                msg.attach(part)
                print(f'Attached file: {filename} ({len(data)} bytes)')
            except Exception as e:
                print(f'Failed to attach {file_path}: {e}')

    try:
        context = ssl.create_default_context()
        
        print(f'Connecting to {smtp_host}:{smtp_port}...')
        
        # Use SSL for port 465, TLS for other ports
        if smtp_port == 465:
            print('Using SSL connection (port 465)')
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                print('Connected via SSL, attempting login...')
                server.login(smtp_user, smtp_pass)
                print('Login successful, sending email...')
                server.send_message(msg)
                print(f'✅ Email sent successfully to {len(email_recipients)} recipients: {", ".join(email_recipients)}')
        else:
            print('Using TLS connection (port 587)')
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                print('Connected, starting TLS...')
                server.starttls(context=context)
                print('TLS started, attempting login...')
                server.login(smtp_user, smtp_pass)
                print('Login successful, sending email...')
                server.send_message(msg)
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
    args = parser.parse_args()
    send_email(args.subject, args.message, args.attach)


if __name__ == '__main__':
    main()


