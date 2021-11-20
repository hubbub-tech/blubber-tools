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

def get_renter_ltv(renter_id):
    ltv = 0.0
    orders = Orders.filter({"renter_id": renter_id})
    for order in orders: ltv += order.reservation._charge
    return ltv

def get_active_orders(renter_id):
    active_orders = []
    orders = Orders.filter({"renter_id": renter_id})

    for order in orders:
        if order.res_date_start < date.today():
            if order.ext_date_end > date.today():
                item = Items.get(order.item_id)
                active_rentals.append(item.name)
    return active_orders

def get_favorite_category(renter_id):
    orders = Orders.filter({"renter_id": renter_id})

    for order in orders:
        item = Items.get(order.item_id)
        tags = Tags.by_item(item)
        for tag in tags:
            if favorites.get(tag.name) is None: favorites[tag.name] = 1
            else: favorites[tag.name] += 1

    favorite_category = "all"
    favorite_count = 0
    for tag_name, count in favorites.items():
        if count > favorite_count and tag_name != "all":
            favorite_count = count
            favorite_category = tag_name
    return favorite_category

def generate_renters_by_ltv_csv():
    users = Users.get_all()
    LTVs = []

    for user in users:
        LTVs.append([
            user.name,
            user.email,
            user.dt_joined,
            user.profile.phone,
            get_renter_ltv(user.id)
        ])
    LTVs.sort(key = lambda user: user[-1])
    today_str = date.today().strftime("%Y-%m-%d")
    data_to_csv(LTVs, filename=f"docs/user-ltv_{today_str}.csv")
    # return LTVs

def get_renter_dashboard(user_id):
    renter = Users.get(user_id)

    if renter:
        orders = Orders.filter({"renter_id": user_id})
        total_num_of_orders = len(orders)

        category = get_favorite_category(user_id)
        active_orders = get_active_orders(user_id)

        total_value_of_orders = get_renter_ltv(user_id)
        conversion_ratio = get_conversion_ratio_user(user_id)

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
                - Most Rented Category: {category}
                - Active Orders: {', '.join(active_orders)}

            +++++++++++++++++++++++++++++++++++++++++++++++

        """
    else:
        return f"This user, id:{user_id}, does not exist."
