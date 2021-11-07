from blubber_orm import Reservations

def _safely_swap_reservation(renter, reservation, swap_item):
    swap_res_dict = {
        "item_id": swap_item.id,
        "renter_id": reservation.renter_id,
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
    swap_reservation = Reservations.filter({
        "item_id": swap_item.id,
        "renter_id": reservation.renter_id,
        "date_started": reservation.date_started,
        "date_ended": reservation.date_ended
    })
    if swap_reservation: swap_reservation, = swap_reservation
    else: swap_reservation = Reservations.insert(swap_res_dict)

    if not swap_item.is_locked:
        swap_item.lock(renter)
        if swap_item.calendar.scheduler(swap_reservation):
            Reservations.delete({
                "item_id": reservation.item_id,
                "renter_id": reservation.renter_id,
                "date_started": reservation.date_started,
                "date_ended": reservation.date_ended
            })
            Reservations.set({
                "item_id": swap_item.id,
                "renter_id": reservation.renter_id,
                "date_started": reservation.date_started,
                "date_ended": reservation.date_ended,
            }, {"is_calendared": True})
            swap_item.unlock()
            print("Successfully swapped reservations...")
            return
        else:
            swap_item.unlock()
            raise Exception("Could not be swapped because item is taken or expired.")
    else:
        raise Exception("Someone else is accessing the item at the moment.")

def address_to_request(address):
    requestable_address = address.display()
    requestable_address = requestable_address.replace(" ", "+")
    return requestable_address
