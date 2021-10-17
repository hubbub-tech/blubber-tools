from datetime import datetime, date, timedelta

from blubber_orm import Users, Orders

from .utils import data_to_csv

def get_renters_by_date_placed(date_placed):
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
