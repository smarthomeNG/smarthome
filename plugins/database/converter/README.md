# convert.py

##Purpose
The purpose of this script is to help you convert your existing sqlite3 data into another database engine.
Currently it supports migrating to MySQL and PostgreSQL

##General usage
You can run `./convert.py -?` or `./convert.py --help` for help

Currently the script supports the following parameters, most of them have default values.
<pre>
-s SOURCE               source database path, default is 'smarthome.db'.
-e {mysql,postgres}     destination database engine, default is 'mysql'.
-h HOST                 destination database host, default is 'localhost'.
-d DATABASE             destination database name, default is 'smarthome'.
-ru ROOTUSER            destination database administrator username, default is 'root'.
-rp ROOTPASSWORD        destination database administrator password.
-u USER                 destination database smarthome username, default is 'smarthome'.
-p PASSWORD             destination database smarthome username, default is 'smarthome'.
</pre>
## MySQL
MySQL conversion has been tested with MariaDB 10.0
### command line
If you are inside the smarthome directory and want to convert your sqlite3 database to mysql a typical command line could be:
`plugins/database/converter/convert.py -s var/db/smarthome.db -e mysql -rp myrootmysqlpassword`

This command would:
* create a database called "smarthome"
* create a user called "smarthome" with password "smarthome"
* grant access for user "smarthome" to newly created database "smarthome"
* create tables in newly created database
* copy content from sqlite3 to new database

### plugin.conf
Typically you would use something similar to the following in your plugin.conf
<pre>
[database]
    class_name = Database
    class_path = plugins.database
    engine = mysql
    database = smarthome
    host = localhost
    username = smarthome
    password = whatever
</pre>

## PostgreSQL
TODO: Test and document postgres migration
