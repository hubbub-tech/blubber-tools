from datetime import datetime, date, timedelta

from blubber_orm import Items

from .utils import data_to_csv

def search_items(search_key):
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
