import psycopg2

from datetime import datetime, date

from blubber_orm import Users
from blubber_orm import Items, Details, Addresses
from blubber_orm import Dropoffs, Pickups, Logistics
from blubber_orm import Orders, Extensions, Reservations

from .utils import _safely_swap_reservation

def exp_decay(retail_price, time_now, discount=.50, time_total=28):
    #Where discount is issued at time_total
    base_price = retail_price / 10
    if time_now > 180:
        time_total = 56
    compound = retail_price / 90
    a = compound * 10 ** (-log((1 - discount), 10) / (time_total - 1))
    r = 1 - (compound / a)
    y = a * (1 - r) ** time_now #per_day_price_now
    #calculate the cost of the rental to the user
    integ_time = y / log(1 - r)
    integ_0 = a * (1 - r) / log(1 - r)
    cost_to_date = base_price + integ_time - integ_0
    if cost_to_date < base_price:
        return base_price
    return cost_to_date

def check_price(duration):
    cost = exp_decay(retail_price=95.00, time_now=duration)
    discounted_cost = cost * 0.65
    return discounted_cost

def swap_order(order_id, swap_item_id):
    order = Orders.get(order_id)
    if order:
        item = Items.get(order.item_id)
        renter = Users.get(order.renter_id)
        reservation = order.reservation

        dropoff = Dropoffs.by_order(order)
        pickup = Pickups.by_order(order)

        dt_dropoff_completed = order.dt_dropoff_completed
        dt_pickup_completed = order.dt_pickup_completed
        print("dt_dropoff_completed", dt_dropoff_completed)
        print("dt_pickup_completed", dt_pickup_completed)

        swap_item = Items.get(swap_item_id)
        _safely_swap_reservation(renter, reservation, swap_item)

        swap_order_dict = {
            "id": order.id,
            "date_placed": order.date_placed,
            "is_online_pay": order.is_online_pay,
            "is_dropoff_sched": order.is_dropoff_scheduled,
            "is_pickup_sched": order.is_pickup_scheduled,
            "lister_id": order.lister_id,
            "item_id": swap_item_id,
            "renter_id": order.renter_id,
            "res_date_start": order.res_date_start,
            "res_date_end": order.res_date_end
        }
        swapped_order = Orders.insert(swap_order_dict)
        # BUG: changes the completion time :(
        if dropoff:
            dropoff.schedule_orders([swapped_order])
            if dt_dropoff_completed:
                order.complete_dropoff(dt_completed=dt_dropoff_completed)
        if pickup:
            pickup.schedule_orders([swapped_order])
            if dt_pickup_completed:
                order.complete_pickup(dt_completed=dt_pickup_completed)

        print(f"Successfully swapped {item.name} for {swap_item.name}.")
    else:
        raise Exception("The order does not exist.")

def swap_extension(order_id, date_ended, swap_item_id):
    order = Orders.get(order_id)
    if order:
        extensions = order.extensions
        res_date_ended = datetime.strptime(date_ended, "%Y-%m-%d").date()

        for extension in extensions:
            if extension.res_date_end == res_date_ended:
                item = Items.get(extension.item_id)
                renter = Users.get(extension.renter_id)
                reservation = extension.reservation

                swap_item = Items.get(swap_item_id)
                _safely_swap_reservation(renter, reservation, swap_item)

                swap_extension_dict = {
                    "order_id": extension.order_id,
                    "item_id": swap_item_id,
                    "renter_id": extension.renter_id,
                    "res_date_start": extension.res_date_start,
                    "res_date_end": extension.res_date_end,
                }
                swap_extension = Extensions.insert(swap_extension_dict)
                print(f"Successfully swapped {item.name} for {swap_item.name}.")
                return
        raise Exception("There aren't any extensions associated with reservation.")
    else:
        raise Exception("The order does not exist.")

def cancel_order(order_id):
    order = Orders.get(order_id)
    if order:
        reservation_keys = {
            "item_id": order.item_id,
            "renter_id": order.renter_id,
            "date_started": order.res_date_start,
            "date_ended": order.res_date_end
        }
        item = Items.get(order.item_id)
        renter = Users.get(order.renter_id)
        reservation = order.reservation

        dropoff = Dropoffs.by_order(order)
        if dropoff: dropoff.cancel(order)

        pickup = Pickups.by_order(order)
        if pickup: pickup.cancel(order)

        Reservations.delete(reservation_keys)
        print("The order or extension has been deleted.")
    else:
        raise Exception("The order does not exist.")

def cancel_extension(order_id, date_ended):
    order = Orders.get(order_id)
    if order:
        extensions = order.extensions
        res_date_ended = datetime.strptime(date_ended, "%Y-%m-%d").date()

        for extension in extensions:
            if extension.res_date_end == res_date_ended:
                pickup = Pickups.by_order(order)
                if pickup: pickup.cancel(order)

                reservation_keys = {
                    "item_id": extension.item_id,
                    "renter_id": extension.renter_id,
                    "date_started": extension.res_date_start,
                    "date_ended": extension.res_date_end
                }
                Reservations.delete(reservation_keys)
                print("The order or extension has been deleted.")
                return
            else:
                print("Searching...")
    raise Exception("The extension does not exist.")
