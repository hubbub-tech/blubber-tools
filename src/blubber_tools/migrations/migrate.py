import csv
import json

from blubber_orm import Addresses
from blubber_orm import Users, Profiles, Carts
from blubber_orm import Items, Details, Calendars
from blubber_orm import Orders, Extensions, Reservations
from blubber_orm import Pickups, Dropoffs, Logistics
from blubber_orm import Tags, Reviews, Testimonials

def csv_to_database(filename):
    with open(filename, mode='r') as spreadsheet:
        reader = csv.DictReader(spreadsheet)
        for row in reader:
            row_to_dict = dict(row)

            print(row_to_dict)

            if "addresses.csv" in filename: Addresses.insert(row_to_dict)
            elif "users.csv" in filename: Users.insert(row_to_dict)
            elif "profiles.csv" in filename: Profiles.insert(row_to_dict)
            elif "carts.csv" in filename: Carts.insert(row_to_dict)
            elif "items.csv" in filename: Items.insert(row_to_dict)
            elif "details.csv" in filename: Details.insert(row_to_dict)
            elif "calendars.csv" in filename: Calendars.insert(row_to_dict)
            elif "reservations.csv" in filename: Reservations.insert(row_to_dict)
            elif "orders.csv" in filename: Orders.insert(row_to_dict)
            elif "tags.csv" in filename: Tags.insert(row_to_dict)

def json_to_database(filename):
    data = json.load(filename)
