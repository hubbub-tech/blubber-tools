from datetime import datetime, date
from blubber_orm import get_db
from blubber_orm import Users
from blubber_orm import Items, Details, Addresses
from blubber_orm import Orders

from .utils import data_to_csv

def get_like_items(search_key):
    items = Items.like("name", f"%{search_key}%")
    targets = []
    for item in items:
        if item.is_available and item.calendar.check_availability():
            targets.append((
                item.id,
                item.name,
                item.address.zip_code,
                f"https://www.hubbub.shop/inventory/i/id={item.id}"
            ))
    if targets: targets.sort(key = lambda item: item[0])
    data_to_csv(targets)
    return targets

def get_renters_by_order_date(date_placed):
    date_placed_obj = datetime.strptime(date_placed, "%Y-%m-%d").date()
    orders_after_date = Orders.get_all()
    targets = []
    for order in orders_after_date:
        if order.date_placed >= date_placed_obj:
            renter = Users.get(order.renter_id)
            targets.append((renter.name, renter.email))
    targets = set(targets)
    data_to_csv(targets)
    return targets
