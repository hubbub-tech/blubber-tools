from blubber_orm import get_db
from blubber_orm import Items, Details, Addresses

def get_like_items(name, zip):
    items = Items.like("name", f"%{name}%")
    targets = []
    for item in items:
        address_zip = item.address.zip_code
        if item.is_available and address_zip > zip:
            if item.calendar.check_availability():
                targets.append((item.id, item.name, item.address.zip_code))
    if targets: targets.sort(key = lambda item: item[0])
    return targets
