"""Console script for idoit_api."""
import sys
import click
import os
from idoit_api.const import LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, LOG_LEVEL_DEBUG
from idoit_api.__about__ import __version__
from idoit_api.base import API

@click.group()
@click.option('-l', '--log-level', default=LOG_LEVEL_INFO, show_default=True)
@click.option('-P', '--permission-level', default=1, show_default=True,
              help="Level of rights for API Operations. Higher level gives more permissions")
def main(permission_level, log_level):
    """Console script for idoit_api"""

    click.echo('Version: {}'.format(__version__))

    return 0


@main.command()
@click.option('--url', prompt=True, envvar='CMDB_URL')
@click.option('-u', '--username', prompt=True, envvar='CMDB_USER')
@click.option('-p', '--password', prompt=True, hide_input=True, envvar='CMDB_PASS')
@click.option('-k', '--api-key', prompt=True, hide_input=True, envvar='CMDB_API_KEY')
def login(url, username, password, api_key):
    api = API(url=url, key=api_key, username=username, password=password)
    if api.login():
        click.echo("Successfully authenticated with the API at {}".format(url))


@main.command()
def reset_credentials():
    if os.environ.get('CMDB_USER'):
        del os.environ['CMDB_USER']
    if os.environ.get('CMDB_PASS'):
        del os.environ['CMDB_PASS']
    if os.environ.get('CMDB_API_KEY'):
        del os.environ['CMDB_API_KEY']
    if os.environ.get('CMDB_URL'):
        del os.environ['CMDB_URL']
    if os.environ.get('CMDB_SESSION_ID'):
        del os.environ['CMDB_SESSION_ID']

# TODO add command to specify login credentials via file


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
