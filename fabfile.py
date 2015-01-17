# Fabric file to do setup
import os
from fabric.api import local


def check_env(function):
    """
    Ensure that the required environment variables are present
    """
    def wrapper(*args, **kwargs):
        assert 'PGHOST' in os.environ
        assert 'PGPASSWORD' in os.environ
        return function(*args, **kwargs)
    return wrapper


def psql(filename, database='analytics', username=None, password=None):
    """
    Execute the given file on the database server
    """
    if username is None:
        username = os.environ['PGUSER']
    if password is None:
        password = os.environ['PGPASSWORD']

    command = ' '.join([
        'PGUSER=%s' % username,
        'PGPASSWORD=%s' % password,
        'psql',
        '-d %s' % database,
        '<', filename
    ])
    return local(command)


def initialize_databases():
    """
    Initialize the jcr databases required for this to work

    See: https://help.pentaho.com/Documentation/5.2/0F0/0K0/030 
    """
    # create_jcr_postgresql
    psql('data/postgresql/create_jcr_postgresql.sql')
    psql('data/postgresql/create_repository_postgresql.sql')
    psql('data/postgresql/create_quartz_postgresql.sql')
    psql('data/postgresql/create_quartz_postgresql2.sql', 'quartz', 'pentaho_user', 'password')


def run():
    """
    Run pentaho BI server
    """
    local('sh $PENTAHO_HOME/biserver-ce/start-pentaho.sh')
