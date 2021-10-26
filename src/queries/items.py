from datetime import datetime, date, timedelta

from blubber_orm import Items

from .reservations import get_cumulative_downtime, get_average_downtime, get_conversion_ratio_item
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

def generate_rental_history(item):
    rental_history = f"""
        ==================================================
            Revenue | start: YYYY-MM-DD, end: YYYY-MM-DD
        ==================================================
    """
    reservations = item.calendar.reservations
    if reservations:
        for reservation in reservations:
            row = "\t    ${:,.2f}".format(reservation._charge)

            start_date = reservation.date_started.strftime("%Y-%m-%d")
            end_date = reservation.date_ended.strftime("%Y-%m-%d")
            row += f" | \t{start_date}       {end_date}\n"
            rental_history += row
    else:
        rental_history += "\t\tNo rental history to date.\n"
    rental_history += "\t=================================================="
    return rental_history

def get_item_dashboard(item_id):
    item = Items.get(item_id)
    rental_history = generate_rental_history(item)
    conversion_ratio = get_conversion_ratio_item(item_id)

    first_listed = item.dt_created.strftime("%B %-d, %Y")
    created_days_ago = (date.today() - item.dt_created.date()).days

    cum_downtime = get_cumulative_downtime(item)
    avg_downtime = get_average_downtime(item)

    reservations = Reservations.filter({ "item_id": item_id })
    if reservations:
        for reservation in reservations:
            if reservation.date_started < date.today():
                if reservation.date_ended > date.today():
                    renter_id = reservation.renter_id
                    renter = Users.get(renter_id)
                    renter_name = f"{renter.name}, id: {renter.id}"
                    break
    else:
        renter_name = "No renter right now."

    print(
    f"""
        ++++++++++++++++++++++++++++++++++++++++++++++++++++++

        Hubbub Shop Stats, Item: {item_id}

            Name: {item.name}
            First Listed: {first_listed}, {created_days_ago} days ago...

            Conversion Ratio: {conversion_ratio}

            Cum. Downtime: {cum_downtime} days
            Avg. Downtime: {avg_downtime} days

            Current Renter: {renter_name}

                        Reservation History
                        {rental_history}

        ++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    )
