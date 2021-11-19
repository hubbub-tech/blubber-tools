import csv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridAPIConfig:
    DEFAULT_SENDER = os.environ["SENDGRID_API_KEY"]
    DEFAULT_RECEIVER = os.environ["DEFAULT_RECEIVER"]
    SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]

SG = SendGridAPIConfig()

def _send_email(to, subject, body):
    msg = Mail(
        from_email=SG.DEFAULT_SENDER,
        to_emails=to,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(SG.SENDGRID_API_KEY)
        response = sg.send(msg)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def request_for_interview(inteview_csv):
    txt_file = open("docs/email_interview_request.txt", "r")
    csv_file = open(inteview_csv, "r")

    raw = txt_file.read(inteview_csv)

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
