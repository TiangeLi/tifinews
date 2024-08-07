from jinja2 import Environment, FileSystemLoader
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from os import getenv
from dotenv import load_dotenv
load_dotenv()

GMAIL_ADDRESS = getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = getenv("GMAIL_PASSWORD")

class EmailSender(object):
    def __init__(self):
        self.sender = GMAIL_ADDRESS
        self.password = GMAIL_PASSWORD
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template = self.env.get_template('modules/email_template.html')

    def send_email(self, subject, body, recipients, debug=False):
        body = self.template.render(body)
        # --- debug template
        if debug:
            with open('test.html', 'w') as f:
                f.write(body)
        # --- end debug
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(recipients)
        with SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(self.sender, self.password)
            smtp_server.sendmail(self.sender, recipients, msg.as_string())
        print("Message sent!")