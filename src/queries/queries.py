import psycopg2

from datetime import datetime, date

from blubber_orm import get_db
from blubber_orm import Users
from blubber_orm import Items, Details, Addresses
from blubber_orm import Dropoffs, Pickups, Logistics
from blubber_orm import Orders, Extensions, Reservations

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

def swap_rental(renter_id, item_id, date_started, date_ended, new_item_id):
    item = Items.get(item_id)
    new_item = Items.get(new_item_id)
    renter = Users.get(renter_id)
    reservation_keys = {
        "item_id": item_id,
        "renter_id": renter_id,
        "date_started": datetime.strptime(date_started, "%Y-%m-%d").date(),
        "date_ended": datetime.strptime(date_ended, "%Y-%m-%d").date()
    }
    reservation = Reservations.get(reservation_keys)
    if reservation:
        new_res_dict = {
            "item_id": new_item_id,
            "renter_id": renter_id,
            "date_started": reservation.date_started,
            "date_ended": reservation.date_ended,
            "is_calendared": False,
            "is_extended": reservation.is_extended,
            "is_in_cart": reservation.is_in_cart,
            "dt_created": reservation.dt_created,
            "charge": reservation._charge,
            "deposit": reservation._deposit,
            "tax": reservation._tax
        }
        search_keys = {
            "res_date_start": reservation.date_started,
            "res_date_end": reservation.date_ended,
            "renter_id": reservation.renter_id,
            "item_id": reservation.item_id
        }
        try:
            new_reservation = Reservations.insert(new_res_dict)
        except psycopg2.errors.UniqueViolation as e:
            Reservations.database.connection.rollback()
            """It's likely that the new reservation has already been created"""
            new_reservation, *_ = Reservations.filter({
                "item_id": new_item_id,
                "renter_id": renter_id,
                "date_started": reservation.date_started,
                "date_ended": reservation.date_ended,
            })
            print(e)
        except psycopg2.errors.InFailedSqlTransaction as e:
            raise e
        except Exception as e:
            raise e
        if reservation.is_calendared and not reservation.is_extended:
            order, *_ = Orders.filter(search_keys)
            new_order_dict = {
                "id": order.id,
                "date_placed": order.date_placed,
                "is_online_pay": order.is_online_pay,
                "is_dropoff_sched": order.is_dropoff_scheduled,
                "is_pickup_sched": order.is_pickup_scheduled,
                "lister_id": order.lister_id,
                "item_id": new_item_id,
                "renter_id": order.renter_id,
                "res_date_start": order.res_date_start,
                "res_date_end": order.res_date_end,
            }
            # Check if someone else is ordering it right now
            if not new_item.is_locked:
                # if not, lock it
                new_item.lock(renter)
                # check if the new reservation is even valid, if yes swap it
                if new_item.calendar.scheduler(new_reservation):
                    Reservations.delete(reservation_keys)
                    Reservations.set({
                        "item_id": new_item_id,
                        "renter_id": renter_id,
                        "date_started": reservation.date_started,
                        "date_ended": reservation.date_ended,
                    }, {"is_calendared": True})
                    new_item.unlock()

                    new_order = Orders.insert(new_order_dict)
                else:
                    new_item.unlock()
                    raise Exception("Could not be swapped because item is taken or expired.")

        elif reservation.is_calendared and reservation.is_extended:
            extension, *_ = Extensions.filter(search_keys)
            new_extension_dict = {
                "order_id": extension.order_id,
                "item_id": new_item_id,
                "renter_id": extension.renter_id,
                "res_date_start": extension.res_date_start,
                "res_date_end": extension.res_date_end,
            }
            if not new_item.is_locked:
                new_item.lock(renter)
                if new_item.calendar.scheduler(new_reservation):
                    Reservations.delete(reservation_keys)
                    Reservations.set({
                        "item_id": new_item_id,
                        "renter_id": renter_id,
                        "date_started": reservation.date_started,
                        "date_ended": reservation.date_ended,
                    }, {"is_calendared": True})
                    new_item.unlock()

                    new_extension = Extensions.insert(new_extension_dict)
                else:
                    new_item.unlock()
                    raise Exception("Could not be swapped because item is taken or expired.")
        else:
            raise Exception("This case means that there aren't any orders or extensions associated with res.")
    else:
        raise Exception("Reservation does not exist.")
    print(f"Successfully swapped {item.name} for {new_item.name}")

def cancel_rental(renter_id, item_id, date_started, date_ended):
    reservation_keys = {
        "item_id": item_id,
        "renter_id": renter_id,
        "date_started": datetime.strptime(date_started, "%Y-%m-%d").date(),
        "date_ended": datetime.strptime(date_ended, "%Y-%m-%d").date()
    }
    item = Items.get(item_id)
    renter = Users.get(renter_id)
    reservation = Reservations.get(reservation_keys)
    if reservation:
        search_keys = {
            "res_date_start": reservation.date_started,
            "res_date_end": reservation.date_ended,
            "renter_id": reservation.renter_id,
            "item_id": reservation.item_id
        }
        if reservation.is_calendared and not reservation.is_extended:
            order, *_ = Orders.filter(search_keys)
            dropoff = Dropoffs.by_order(order)
            if dropoff: dropoff.cancel(order)
        elif reservation.is_calendared and reservation.is_extended:
            extension, *_ = Extensions.filter(search_keys)
            order = extension.order
        pickup = Pickups.by_order(order)
        if pickup: pickup.cancel(order)

        Reservations.delete(reservation_keys)
        print("The order or extension has been deleted.")
    else:
        raise Exception("Reservation does not exist.")
