import psycopg2
import requests

from blubber_orm import Users, Items
from blubber_orm import Addresses

from .utils import address_to_request

# Environment Variables
GOOGLE_GEOCODE_KEY = os.environ.get("GOOGLE_GEOCODE_KEY")

def swap_user_address(user_id, num, street, city, state, zip, apt=""):
    user = Users.get(user_id)
    address_keys = {
        "num": num,
        "street": street,
        "city": city,
        "state": state,
        "zip": zip,
        "apt": apt
    }
    address = Addresses.filter(address_keys)
    if address: address, = address
    else: address = Addresses.insert(address_keys)

    if user:
        Users.set({"id": user_id}, {
            "address_num": num,
            "address_street": street,
            "address_apt": apt,
            "address_zip": zip
        })
    else:
        raise Exception(f"This user, id: {user_id}, does not exist.")

def swap_item_address(item_id, num, street, city, state, zip, apt=""):
    item = Items.get(item_id)
    address_keys = {
        "num": num,
        "street": street,
        "city": city,
        "state": state,
        "zip": zip,
        "apt": apt
    }
    address = Addresses.filter(address_keys)
    if address: address, = address
    else: address = Addresses.insert(address_keys)

    if item:
        Items.set({"id": item_id}, {
            "address_num": num,
            "address_street": street,
            "address_apt": apt,
            "address_zip": zip
        })
    else:
        raise Exception(f"This item, id: {item_id}, does not exist.")

def get_geocode_json(num, street, apt, zip):
    address = Addresses.get({
        "num": num,
        "street": street,
        "apt": apt,
        "zip":zip
    })
    ADDRESS = address_to_request(address)
    URL = f"https://maps.googleapis.com/maps/api/geocode/json?address={ADDRESS}&key={GOOGLE_GEOCODE_KEY}"
    response = requests.get(URL)
    return response.json()
