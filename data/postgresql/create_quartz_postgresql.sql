--Begin--
-- note: this script assumes pg_hba.conf is configured correctly
--

-- \connect postgres postgres

drop database if exists quartz;
drop user if exists pentaho_user;

CREATE USER pentaho_user PASSWORD 'password';
GRANT pentaho_user TO pentaho;

CREATE DATABASE quartz  WITH OWNER = pentaho_user  ENCODING = 'UTF8';

GRANT ALL ON DATABASE quartz to pentaho_user;

--End--
