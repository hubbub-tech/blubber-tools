import click

from .emails import request_for_interview

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

email_interface.add_command(interview)
