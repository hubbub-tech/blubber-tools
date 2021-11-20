import os
import csv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridAPIConfig:
    DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
    DEFAULT_RECEIVER = os.environ["MAIL_DEFAULT_RECEIVER"]

    SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]

    DEFAULT_SENDER_NAME = "Ade Balogun"
    DEFAULT_RECEIVER_NAME = "Ade Balogun"

SG = SendGridAPIConfig()

def _send_email(to, subject, body):
    msg = Mail(
        from_email=(SG.DEFAULT_SENDER, SG.DEFAULT_SENDER_NAME),
        to_emails=to,
        subject=subject,
        html_content=body
    )
    msg.cc = SG.DEFAULT_RECEIVER
    try:
        sg = SendGridAPIClient(SG.SENDGRID_API_KEY)
        response = sg.send(msg)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def request_for_interview(inteview_csv):
    txt_file = open("../docs/request_for_interview.txt", "r")
    csv_file = open(f"../docs/{inteview_csv}", "r")

    raw = txt_file.read()

    csv_reader = csv.reader(csv_file, delimiter=',')
    for user in csv_reader:
        user_email = user[1]
        user_name = user[0] # @notice: returns the name
        first_name, last_name, *_ = user_name.split(" ")

        body = raw.replace("{NAME}", first_name)
        _send_email(
            to=user_email,
            subject="Can we chat for 15 minutes sometime?",
            body=body
        )

    csv_file.close()
    txt_file.close()
