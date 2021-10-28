from time import sleep
from manage import swap_order, cancel_order
from queries import get_renter_dashboard, get_item_dashboard

user_id = input("Which user id would you like stats on? ")
get_renter_dashboard(user_id=user_id)
