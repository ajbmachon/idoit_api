import getpass
import os
import builtins


def cli_login_prompt():
    """Saves API authentication credentials in environmental variables
    """
    cmdb_user = os.environ.get('CMDB_USER')
    cmdb_pass = os.environ.get('CMDB_PASS')
    api_key = os.environ.get('CMDB_API_KEY')
    url = os.environ.get('CMDB_URL')

    if not cmdb_user:
        cmdb_user = input("CMDB Username: ")
        os.environ['CMDB_USER'] = cmdb_user
    if not cmdb_pass:
        cmdb_pass = getpass.getpass(prompt="CMDB Password: ")
        os.environ['CMDB_PASS'] = cmdb_pass
    if not api_key:
        api_key = getpass.getpass(prompt="CMDB API key: ")
        os.environ['CMDB_API_KEY'] = api_key
    if not url:
        url = input("CMDB URL [https://cmdb.example.de/src/jsonrpc.php]: ", )
        os.environ['CMDB_URL'] = url or "https://cmdb.example.de/src/jsonrpc.php"

