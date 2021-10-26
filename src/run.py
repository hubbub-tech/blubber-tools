from time import sleep
from manage import swap_order, cancel_order
from queries import get_renter_dashboard, get_item_dashboard

item_id = input("Which item id would you like stats on? ")
get_item_dashboard(item_id=item_id)
