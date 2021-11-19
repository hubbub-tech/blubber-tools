import pytz
import random

from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

def generate_date_range(min=date.today(), max=date.max):
    time_between_dates = max - min
    days_between_dates = time_between_dates.days
    random_duration = random.randrange(days_between_dates)
    random_offset = random.randrange(days_between_dates)
    while random_duration + random_offset >= days_between_dates:
        random_duration = random.randrange(days_between_dates)
        random_offset = random.randrange(days_between_dates)
    random_start_date = min + timedelta(days=random_offset)
    random_end_date = random_start_date + timedelta(days=random_duration)
    return random_start_date, random_end_date

def generate_tag_dict():
    tag = random.choice(tags)
    return {"tag_name": tag}

def generate_identity_dict():
    firstname = random.choice(firstnames)
    lastname = random.choice(lastnames)
    name = f"{firstname},{lastname}"
    email = f"fake_{firstname.lower()[0]}-{lastname.lower()}@hubbub.shop"
    payment = f"@{firstname[0]}-{lastname}-1"
    phone = f"732{random.randint(100, 999)}{random.randint(100, 999)}0"
    bio = "I love Hubbub!"
    address = generate_address_dict()
    return {
        "user": {
            "name": name,
            "email": email,
            "dt_joined": datetime.now(tz=pytz.UTC),
            "dt_last_active": datetime.now(tz=pytz.UTC),
            "is_blocked": False,
            "payment": payment,
            "password": generate_password_hash("password"),
            "address_num": address["num"],
            "address_street": address["street"],
            "address_apt": address["apt"],
            "address_zip": address["zip"]
        },
        "profile": {
            "phone": phone,
            "bio": bio,
            "has_pic": False
        },
        "cart": {
            "total":0
        },
        "address": address
        }

def generate_address_dict():
    num = random.randint(1, 99)
    street = random.choice(streets)
    street_suffix = random.choice(street_suffixes)
    apt = ""
    city = "New York"
    state = "NY"
    zip = f"100{random.randint(10, 99)}"
    return {
        "num": num,
        "street": street + " " + street_suffix,
        "apt": apt,
        "city": city,
        "state": state,
        "zip": zip}

def generate_item_dict():
    item_name = random.choice(items)
    start_date, end_date = generate_date_range(max=date(2025, 12, 31))
    address = generate_address_dict()
    return {
        "item": {
            "lister_id" : 1,
            "name" : item_name,
            "price" : random.randint(100, 400) + .99,
            "is_available": True,
            "is_featured": False,
            "dt_created": datetime.now(tz=pytz.UTC),
            "is_locked": False,
            "last_locked": None,
            "is_routed": False,
            "address_num": address["num"],
            "address_street": address["street"],
            "address_apt": address["apt"],
            "address_zip": address["zip"]
        },
        "details": {
            "description" : "This is just for lols.",
            "condition" : random.randint(1, 3),
            "volume" : random.randint(1, 3),
            "weight" : random.randint(1, 3)
        },
        "calendar": {
            "date_started" : start_date,
            "date_ended" : end_date
        },
        "address": address
    }
