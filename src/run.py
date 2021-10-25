from time import sleep
from manage import swap_order, cancel_order
from queries import get_value_to_date

user_id = input("Which user id would you like stats on? ")
get_value_to_date(user_id=user_id)
