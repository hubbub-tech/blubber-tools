import click

from .users import get_renter_dashboard, generate_renters_by_ltv_csv
from .items import get_item_dashboard

@click.command('dashboard')
@click.option('--item', default=None, help='id of the item that you want to view')
@click.option('--user', default=None, help='id of the user that you want to view')
def dashboard(item, user):
    """

    Produces a dashboard summarizing metrics on a given item or user, for example:

        blubber dashboard --user=2

    """

    if item and user: click.echo("Error: please select either an item or user to query."); return
    elif item: dashboard = get_item_dashboard(item)
    elif user: dashboard = get_renter_dashboard(user)
    else: click.echo("Error: you didn't query anything. Try 'blubber dashboard --item=1'"); return

    click.echo(dashboard)

@click.group('users')
def users_interface():
    "An interface for running queries on users."

@click.command('lfv')
def lfv():
    lfv = generate_renters_by_ltv_csv()
    click.echo("A lifetime value csv has been generated in the repository's root directory.")

users_interface.add_command(lfv)
