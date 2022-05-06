import click

from .emails import request_for_interview
from .emails import upcoming_pickup_notice

from .rentals import cancel_order

@click.group("email")
def email_interface():
    """Email users with a custom command-line operation."""


# @param: file -- the file to read from
@click.command("interview")
@click.option('-f', '--file', help='Read list of users to email from a csv file')
def interview(file):
    """Request interviews of each user from a list of users."""

    assert file[-4:] == '.csv', 'the file must be a csv file type'
    request_for_interview(file)


@click.command("pickup-notice")
def pickup_notice():
    """Request interviews of each user from a list of users."""

    upcoming_pickup_notice()

# --------------------

@click.group("rentals")
def rentals_interface():
    """Commands pertaining to rental management at admin level."""


@click.command("cancel")
@click.option('-o', '--order', help='Provide the order_id you would like to cancel.')
def cancel_order_tool(order):
    """Specify an order to cancel."""

    cancel_order(order)

# --------------------

@click.command("test")
def test():
    """Say hello."""

    click.echo("Welcome to Blubber Tools.")


email_interface.add_command(test)
email_interface.add_command(interview)
email_interface.add_command(pickup_notice)

rentals_interface.add_command(cancel_order_tool)
