import click

from blubber_orm import get_db

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
