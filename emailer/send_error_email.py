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
        # Best effort print so CI logs show the issue
        print('SMTP credentials are not set; skipping email send.')
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to
    msg.set_content(message)

    # Attach files if provided
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                filename = os.path.basename(file_path)
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
            except Exception as e:
                print('Failed to attach', file_path, e)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        print('Error email sent to', email_to)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', required=True)
    parser.add_argument('--message', required=True)
    parser.add_argument('--attach', action='append', default=[])
    args = parser.parse_args()
    send_email(args.subject, args.message, args.attach)


if __name__ == '__main__':
    main()


