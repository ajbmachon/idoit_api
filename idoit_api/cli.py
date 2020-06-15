"""Console script for idoit_api."""
import sys
import click
import os

from idoit_api.const import LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, LOG_LEVEL_DEBUG
from idoit_api.__about__ import __version__
from idoit_api.requests import IdoitEndpoint
from idoit_api.base import API
from idoit_api.utils import del_env_credentials, cli_login_prompt, parse_env_file_to_vars


@click.group()
@click.option('--debug', default=False)
@click.option('-l', '--log-level', default=LOG_LEVEL_INFO, show_default=True)
@click.option('-P', '--permission-level', default=10, show_default=True,
              help="Level of rights for API Operations. Higher level gives more permissions")
@click.option('--env-file', type=str)
@click.pass_context
def main(ctx, permission_level, log_level, debug, env_file):
    """Console script for idoit_api"""

    ctx.ensure_object(dict)
    ctx.obj['permission_level'] = permission_level
    ctx.obj['log_level'] = log_level
    ctx.obj['debug'] = debug

    click.secho('idoit API Client Version: {}'.format(__version__), fg='green')

    if '--help' not in sys.argv:
        if env_file:
            parse_env_file_to_vars(env_file)
            api = API(**ctx.obj)
            api.login()
        if not os.environ.get('CMDB_SESSION_ID'):
            cli_login_prompt()
            api = API(**ctx.obj)
            api.login()

    return 0


@main.command()
@click.option('--url', prompt=True, envvar='CMDB_URL')
@click.option('-u', '--username', prompt=True, envvar='CMDB_USER')
@click.option('-p', '--password', prompt=True, hide_input=True, envvar='CMDB_PASS')
@click.option('-k', '--api-key', prompt=True, hide_input=True, envvar='CMDB_API_KEY')
@click.pass_obj
@click.help_option
def login(obj, url, username, password, api_key):
    api = API(url=url, key=api_key, username=username, password=password, **obj.copy())
    if api.login():
        click.echo("Successfully authenticated with the API at {}".format(url))


@main.command()
def reset_credentials():
    click.echo("Credentials were reset and deleted from env variables")
    return del_env_credentials()


@main.command()
@click.argument('query', type=str)
@click.option('-m', '--mode', default='normal', type=click.Choice(['normal', 'deep', 'auto-deep']))
@click.pass_obj
def search(obj, query, mode):
    ep = IdoitEndpoint(**obj)
    click.echo(ep.search(query, mode))


@main.command()
@click.pass_obj
def version(obj):
    ep = IdoitEndpoint(**obj)
    click.secho("CMDB Version: {}".format(ep.version), fg='green')
    click.secho("CMDB Version Type: {}".format(ep.version_type), fg='green')


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
