import click

from .emails import email_interview_request

@click.group("email")
def email_interface():
    """Email users with a custom command-line operation."""

# @param: file -- the file to read from
@click.command("interview")
@click.option('-f', '--file', help='Read list of users to email from a csv file')
def interview(file):
    """Request interviews of each user from a list of users."""

    assert file[-4:] == '.csv', 'the file must be a csv file type'
    email_interview_request(file)
