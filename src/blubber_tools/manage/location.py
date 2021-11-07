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

def swap_logistics_address(logistics_keys, num, street, city, state, zip, apt=""):
    logistics = Logistics.get(logistics_keys)
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

    if logistics:
        Logistics.set({
            "dt_sched": logistics.dt_scheduled,
            "renter_id": logistics.renter_id}, {
            "address_num": num,
            "address_street": street,
            "address_apt": apt,
            "address_zip": zip
        })
    else:
        raise Exception(f"This logsitics, for renter_id: {logistics.renter_id}, does not exist.")

def rename_address(curr_address, new_address):
    users = Users.by_address(curr_address)
    items = Items.by_address(curr_address)
    logistics = Logistics.by_address(curr_address)
    for user in users:
        swap_user_address(
            user_id=user.id,
            num=new_address.num,
            street=new_address.street,
            city=new_address.city,
            state=new_address.state,
            zip=new_address.zip_code,
            apt=new_address.apt
        )
    for item in items:
        swap_item_address(
            item_id=item.id,
            num=new_address.num,
            street=new_address.street,
            city=new_address.city,
            state=new_address.state,
            zip=new_address.zip_code,
            apt=new_address.apt
        )
    for event in logistics:
        swap_logistics_address(
            logistics_keys={
                "dt_sched": logistics.dt_scheduled,
                "renter_id": logistics.renter_id
            },
            num=new_address.num,
            street=new_address.street,
            city=new_address.city,
            state=new_address.state,
            zip=new_address.zip_code,
            apt=new_address.apt
        )

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

def get_travel_time(origin, destination):
    origin_response = get_geocode_json(
        origin.num,
        origin.street,
        origin.apt,
        origin.zip
    )
    destination_response = get_geocode_json(
        destination.num,
        destination.street,
        destination.apt,
        destination.zip
    )
    # check if responses are valid
    # pull long and lat from responses and run them through maps API
        # calculate travel time [and another function to return distance]
    return travel_time
