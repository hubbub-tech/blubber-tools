import os
import csv

from datetime import datetime, date
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from blubber_orm import Reservations, Items, Users

class SendGridAPIConfig:
    DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
    DEFAULT_RECEIVER = os.environ["MAIL_DEFAULT_RECEIVER"]

    SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]

    DEFAULT_SENDER_NAME = "Caro from Hubbub"

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

def upcoming_pickup_notice():
    txt_file = open("../docs/upcoming_pickup_notice.txt", "r")
    raw = txt_file.read()

    outstanding_reservations = {}
    reservations = Reservations.filter({"is_calendared": True})

    for reservation in reservations:
        if reservation.date_started < date.today():
            if reservation.date_ended > date.today():
                if outstanding_reservations.get(reservation.renter_id) is None:
                    outstanding_reservations[reservation.renter_id] = []
                outstanding_reservations[reservation.renter_id].append(reservation)

    for renter_id, reservations in outstanding_reservations.items():
        renter = Users.get({"id": renter_id})

        memo_items = []
        links = []
        for reservation in reservations:
            if reservation.item_id not in memo_items:
                item = Items.get({"id": reservation.item_id})
                res_date_end = reservation.date_ended.strftime("%m/%d/%Y")
                link_scaffold = f"<a href='https://www.hubbub.shop/inventory/i/id={item.id}'>{item.name}</a> on {res_date_end}"
                links.append(link_scaffold)
            links_str = ", ".join(links)
        body = raw.replace("{NAME}", renter.name)
        body = body.replace("{LINKS}", links_str)

        _send_email(
            to=renter.email,
            subject="[Hubbub] Scheduling pickups for your rentals",
            body=body
        )
