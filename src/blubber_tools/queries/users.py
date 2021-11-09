from datetime import datetime, date, timedelta

from blubber_orm import Users, Orders, Tags, Items

from .reservations import get_conversion_ratio_user
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

def get_renter_dashboard(user_id):
    renter = Users.get(user_id)

    if renter:
        orders = Orders.filter({"renter_id": user_id})
        total_num_of_orders = 0
        total_value_of_orders = 0.0

        conversion_ratio = get_conversion_ratio_user(user_id)

        favorites = {}
        active_rentals = []

        for order in orders:
            item = Items.get(order.item_id)

            total_num_of_orders += 1
            total_value_of_orders += order.reservation._charge

            if order.res_date_start < date.today():
                if order.ext_date_end > date.today():
                    active_rentals.append(item.name)

            tags = Tags.by_item(item)
            for tag in tags:
                if favorites.get(tag.name) is None:
                    favorites[tag.name] = 1
                else:
                    favorites[tag.name] += 1

        favorite_item = "all"
        favorite_count = 0
        for tag_name, count in favorites.items():
            if count > favorite_count and tag_name != "all":
                favorite_count = count
                favorite_item = tag_name

        user_since = renter.dt_joined.strftime("%B %-d, %Y")
        joined_days_ago = (date.today() - renter.dt_joined.date()).days

        return f"""
            +++++++++++++++++++++++++++++++++++++++++++++++

            Hubbub Shop Stats, User: {user_id}

                Name: {renter.name}
                User Since: {user_since}, {joined_days_ago} days ago...

                Orders-to-Date: {total_num_of_orders}
                Lifetime Value: ${total_value_of_orders}

                Conversion Ratio: {conversion_ratio}

                Rental Activity
                - Most Rented Category: {favorite_item}
                - Active Rentals: {', '.join(active_rentals)}

            +++++++++++++++++++++++++++++++++++++++++++++++

        """
    else:
        return f"This user, id:{user_id}, does not exist."
