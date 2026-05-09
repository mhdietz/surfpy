"""
evaluation/send_report.py

Emails the generated report.html as an HTML attachment via Gmail SMTP.

Requires environment variables:
    GMAIL_USER         — sending Gmail address (e.g. yourname@gmail.com)
    GMAIL_APP_PASSWORD — 16-character app password from Google account settings

Usage:
    python send_report.py
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

RECIPIENTS = [
    'martinhdietz@gmail.com',
    'stefanogscotti@gmail.com',
]

REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.html')


def main():
    gmail_user     = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        print("GMAIL_USER and GMAIL_APP_PASSWORD must be set.")
        sys.exit(1)

    if not os.path.exists(REPORT_PATH):
        print(f"report.html not found at {REPORT_PATH} — run evaluate.py first.")
        sys.exit(1)

    with open(REPORT_PATH, 'rb') as f:
        report_bytes = f.read()

    today   = datetime.now().strftime('%B %d, %Y')
    subject = f"SLAPP Wave Report — {today}"

    msg            = MIMEMultipart()
    msg['From']    = gmail_user
    msg['To']      = ', '.join(RECIPIENTS)
    msg['Subject'] = subject

    msg.attach(MIMEText(
        "Weekly NDBC vs Surfline evaluation attached.\n"
        "Open the HTML file in a browser to view the charts.",
        'plain'
    ))

    attachment = MIMEBase('text', 'html')
    attachment.set_payload(report_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='slapp_report.html')
    msg.attach(attachment)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(gmail_user, gmail_password)
        smtp.sendmail(gmail_user, RECIPIENTS, msg.as_string())

    print(f"Report sent to: {', '.join(RECIPIENTS)}")


if __name__ == '__main__':
    main()
