from time import sleep
from migrations import insert_in_database

insert_in_database("src/migrations/history/items.csv")
sleep(5)
insert_in_database("src/migrations/history/details.csv")
sleep(5)
insert_in_database("src/migrations/history/calendars.csv")
sleep(5)
insert_in_database("src/migrations/history/reservations.csv")
sleep(5)
insert_in_database("src/migrations/history/orders.csv")
