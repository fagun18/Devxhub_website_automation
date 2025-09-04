import os
import ssl
import argparse
import smtplib
from email.message import EmailMessage
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

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = ', '.join(email_recipients)
    msg.set_content(message)

    # Attach files if provided
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                filename = os.path.basename(file_path)
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
                print(f'Attached file: {filename}')
            except Exception as e:
                print(f'Failed to attach {file_path}: {e}')

    try:
        context = ssl.create_default_context()
        
        # Use SSL for port 465, TLS for other ports
        if smtp_port == 465:
            print('Using SSL connection (port 465)')
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                print(f'✅ Email sent successfully to {len(email_recipients)} recipients: {", ".join(email_recipients)}')
        else:
            print('Using TLS connection (port 587)')
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_pass)
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
    except Exception as e:
        print(f'❌ Unexpected error: {e}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', required=True)
    parser.add_argument('--message', required=True)
    parser.add_argument('--attach', action='append', default=[])
    args = parser.parse_args()
    send_email(args.subject, args.message, args.attach)


if __name__ == '__main__':
    main()


