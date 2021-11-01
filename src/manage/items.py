from blubber_orm import Items, Calendars, Reservations

from queries.utils import reservation_sort

def edit_calendar_start(item):
    reservations = item.calendar.reservations
    if reservations:
        reservation_sort(reservations)
        first_reservation = reservations.pop(0)
        new_date_start = first_reservation.date_started
        if item.calendar.date_started > new_date_start:
            Calendars.set(item.id, { "date_started": new_date_start })
