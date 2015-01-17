# Fabric file to do setup
import os
import xml.etree.ElementTree as ET
from fabric.api import local

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

def _configure_hibernate():
    """
    Configure hibernate to use postgres
    """
    # Step 1: Configure settings to use postgres config file
    settings_file = os.path.join(
        os.environ['PENTAHO_HOME'],
        'biserver-ce/pentaho-solutions/system/hibernate/hibernate-settings.xml'
    )
    config = ET.parse(settings_file)
    config_file_path_el = config.find('config-file')
    config_file_path_el.text = 'system/hibernate/postgresql.hibernate.cfg.xml'
    config.write(settings_file)

    # Step 2: Configure the postgres config to use settings from env
    postgres_settings_file = os.path.join(
        os.environ['PENTAHO_HOME'],
        'biserver-ce/pentaho-solutions/system/hibernate/postgresql.hibernate.cfg.xml'
    )
    config = ET.parse(postgres_settings_file)
    config.find(".//property[@name='connection.url']").text = ''.join([
        'jdbc:postgresql://',
        os.environ['PGHOST'] + ':' + os.environ.get('PGPORT', '5432'),
        '/hibernate'
    ])
    config.find(".//property[@name='connection.username']").text = os.environ['PGUSER']
    config.find(".//property[@name='connection.password']").text = os.environ['PGPASSWORD']
    config.write(postgres_settings_file)
    
def _configure_jackrabbit():
    """
    configure jackrabbit to use postgres
    """
    url = 'jdbc:postgresql://%s:%s/jackrabbit' % (
        os.environ['PGHOST'],
        os.environ.get('PGPORT', '5432'),
    )
    config = ET.parse('config/jackrabbit_repository.xml')
    for url_param in config.findall(".//param[@name='url']"):
        url_param.set('value', url)
    config.write(
        os.path.join(
            os.environ['PENTAHO_HOME'],
            'biserver-ce/pentaho-solutions/system/jackrabbit/repository.xml'
        )
    )


def configure_repository():
    """
    Configure the database server on the config files

    See: https://help.pentaho.com/Documentation/5.2/0F0/0K0/040
    """
    _configure_hibernate()
    _configure_jackrabbit()

def run():
    """
    Run pentaho BI server
    """
    configure_repository()
    local('sh $PENTAHO_HOME/biserver-ce/start-pentaho.sh')
