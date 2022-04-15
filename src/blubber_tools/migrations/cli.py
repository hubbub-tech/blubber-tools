import click

from blubber_orm import get_db
from blubber_orm import Users, Profiles, Carts, Items, Details, Calendars, Addresses

@click.group("migrate")
def migrate_interface():
    """Interface for migrating data into the database."""

@click.command("create")
@click.option("-f", "--file", help="path to the database schema, a SQL file")
def create_database(file):
    try:
        database = get_db()
        database.cursor.execute(open(f"docs/{file}", "r").read())
    except FileNotFoundError as no_create_sql_present:
        print(no_create_sql_present)
    except Exception as e:
        print(e)
    else:
        print("Successfully created Hubbub database.")

@click.command("destroy")
@click.option("-f", "--file", help="path to database desctruction, a SQL file")
def destroy_database(file):
    try:
        database = get_db()
        database.cursor.execute(open(f"docs/{file}", "r").read())
    except FileNotFoundError as no_destroy_sql_present:
        print(no_destroy_sql_present)
    except Exception as e:
        print(e)
    else:
        print("Successfully destroyed Hubbub database.")

@click.command("fake")
@click.option("-u", "--users", help="number of users you would like to generate.")
@click.option("-i", "--items", help="number of items you would like to generate.")
def fudge_data(users, items):
    i = 0
    while i < users:
        scaffold = generate_identity_dict()

        db_address = Addresses.insert(scaffold['address'])

        db_user = Users.insert(scaffold['user'])
        db_cart = Carts.insert(scaffold['cart'])
        db_profile = Profiles.insert(scaffold['profile'])

    i = 0
    while i < items:
        scaffold = generate_item_dict()

        db_address = Addresses.insert(scaffold['address'])

        db_item = Items.insert(scaffold['item'])
        db_details = Details.insert(scaffold['details'])
        db_calendar = Calendars.insert(scaffold['calendar'])
