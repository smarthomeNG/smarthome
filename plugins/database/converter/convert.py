#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Serge Wagener                               serge@swa.lu
#########################################################################
#  This file is part of SmartHome.py.                https://git.io/voaH9
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import argparse
import sqlite3
import os.path
import warnings
import subprocess
import time
import sys

loglevel = 0  # 0 = debug, 1 = info, 2 = warning, 3 = error
tmysql = True
tpostgres = True

try:
    import pymysql.cursors
except:
    print("PyMySQL not installed, please run 'pip3 install PyMySQL' if you want to use mysql as target")
    tmysql = False

try:
    import psycopg2
except:
    print("Psycopg2 not installed, please run 'pip3 install psycopg2' if you want to use postgres as target")
    tpostgres = False


def _log(level, text):
    if level >= loglevel:
        print(text)


def _convert_postgres(args):
    print("Converting sqlite3 '{0}' -> postgres '{1}'.".format(args.source, args.database))
    try:
        print("Creating postgres database {0} and user '{1}'".format(args.database, args.user))
        rc = subprocess.call("sudo -u postgres dropdb {0}".format(args.database), shell=True)
        rc = subprocess.call("sudo -u postgres dropuser {0}".format(args.user), shell=True)
        rc = subprocess.call("sudo -u postgres psql -c \"CREATE USER {0} WITH PASSWORD '{1}';\"".format(args.user, args.password), shell=True)
        rc = subprocess.call("sudo -u postgres createdb {0} -O {1}".format(args.database, args.user), shell=True)
    except:
        _log(3, "Error creating postgres user and database: {0}".format(e))
        return False

    try:
        _log(1, "Connecting to postgres server.")
        con = psycopg2.connect(host=args.host, dbname=args.database, user=args.user, password=args.password)
        cur = con.cursor()
    except psycopg2.OperationalError as e:
        _log(3, "Error connecting to postgres: {0}".format(e))
        return False

    # Creating tables
    try:
        _log(1, "Creating tables in destination database")
        _log(0, "Creating table 'cache'")
        cur.execute("CREATE TABLE cache (_item VARCHAR(255) NOT NULL, \
                                         _start BIGINT, \
                                         _value DOUBLE PRECISION, \
                                         PRIMARY KEY (_item));")
        _log(0, "Creating table 'num'")
        cur.execute("CREATE TABLE num (id SERIAL, \
                                       _start BIGINT, \
                                       _item VARCHAR(255), \
                                       _dur BIGINT, \
                                       _avg DOUBLE PRECISION, \
                                       _min DOUBLE PRECISION, \
                                       _max DOUBLE PRECISION, \
                                       _on DOUBLE PRECISION, \
                                       PRIMARY KEY (id));")
        con.commit()
    except pymysql.err.OperationalError as e:
        _log(3, "Error creating tables: {0}".format(e))
        con.close()
        return False

    # Start conversion
    try:
        _log(1, "Converting data.")
        _log(0, "Connecting to sqlite3 database.")
        sql3con = sqlite3.connect(args.source)
        sql3cur = sql3con.cursor()
        _log(0, "Converting cache table.")
        sql3cur.execute('SELECT _item, _start, _value FROM cache')
        rows = sql3cur.fetchall()
        for row in rows:
            cur.execute("INSERT INTO cache (_item,_start,_value) VALUES ('{0}',{1},{2});".format(row[0], row[1], row[2]))
        con.commit()
        # Converting num table
        _log(0, "Converting num table.")
        sql3cur.execute('SELECT _start, _item, _dur, _avg, _min, _max, _on FROM num')
        rows = sql3cur.fetchall()
        for row in rows:
            cur.execute("INSERT INTO num (_start, _item, _dur, _avg, _min, _max, _on) VALUES ({0},'{1}',{2},{3},{4},{5},{6});"
                        .format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        con.commit()
        sql3con.close()
    except pymysql.err.OperationalError as e:
        _log(3, "Error converting data: {0}".format(e))
        con.close()
        return False
    con.close()
    return True


def _convert_mysql(args):
    print("Converting sqlite3 '{0}' -> mysql '{1}'.".format(args.source, args.database))
    start = time.time()
    try:
        _log(1, "Connecting to mysql server.")
        con = pymysql.connect(host=args.host,
                              user=args.rootuser,
                              password=args.rootpassword,
                              charset='utf8',
                              cursorclass=pymysql.cursors.DictCursor)
    except pymysql.err.OperationalError as e:
        _log(3, "Error connecting to mysql: {0}".format(e))
        return False

    # Create database, drop existing one
    try:
        _log(1, "Creating database replacing existing one if present.")
        warnings.filterwarnings("ignore", "Can't drop database.*")
        cur = con.cursor()
        cur.execute('drop database if exists {0}'.format(args.database))
        cur.execute('create database {0} character set utf8'.format(args.database))
    except pymysql.err.OperationalError as e:
        _log(3, "Error creating database: {0}".format(e))
        con.close()
        return False

    # Create user and grant access
    try:
        _log(1, "Creating user '{0}' and granting access to database '{1}'.".format(args.user, args.database))
        cur.execute("grant all on `" + args.database + "`.* to '{0}'@'%' identified by '{1}'".format(args.user, args.password))
    except pymysql.err.OperationalError as e:
        _log(3, "Error creating user: {0}".format(e))
        con.close()
        return False

    # Creating tables
    try:
        _log(1, "Creating tables in destination database")
        cur.execute("use `" + args.database + "`")
        _log(0, "Creating table 'cache'")
        cur.execute("CREATE TABLE cache (_item VARCHAR(255) NOT NULL, \
                                         _start BIGINT, \
                                         _value DOUBLE, \
                                         PRIMARY KEY (_item)) \
                                         COLLATE utf8_general_ci;")
        _log(0, "Creating table 'num'")
        cur.execute("CREATE TABLE num (id BIGINT NOT NULL AUTO_INCREMENT, \
                                       _start BIGINT, \
                                       _item VARCHAR(255), \
                                       _dur BIGINT, \
                                       _avg DOUBLE, \
                                       _min DOUBLE, \
                                       _max DOUBLE, \
                                       _on DOUBLE, \
                                       PRIMARY KEY (id)) \
                                       COLLATE utf8_general_ci;")
        con.commit()
    except pymysql.err.OperationalError as e:
        _log(3, "Error creating tables: {0}".format(e))
        con.close()
        return False

    # Start conversion
    try:
        _log(1, "Converting data.")
        _log(0, "Connecting to sqlite3 database.")
        sql3con = sqlite3.connect(args.source)
        sql3cur = sql3con.cursor()
        _log(0, "Converting cache table.")
        sql3cur.execute('SELECT _item, _start, _value FROM cache')
        rows = sql3cur.fetchall()
        for row in rows:
            cur.execute("INSERT INTO cache (_item, _start, _value) VALUES ('{0}', {1}, {2});".format(row[0], row[1], row[2]))
        con.commit()
        # Converting num table
        _log(0, "Converting num table (prints a dot every 1000 rows).")
        sql3cur.execute('SELECT _start, _item, _dur, _avg, _min, _max, _on FROM num')
        rows = sql3cur.fetchall()
        con.autocommit(False)
        count = 0
        for row in rows:
            cur.execute("INSERT INTO num (_start, _item, _dur, _avg, _min, _max, _on) VALUES ({0},'{1}',{2},{3},{4},{5},{6});"
                        .format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            count += 1
            if count % 1000 == 0:
                print('.', end='')
                sys.stdout.flush()
        print('')
        con.commit()
        sql3con.close()
    except pymysql.err.OperationalError as e:
        _log(3, "Error converting data: {0}".format(e))
        con.close()
        return False
    con.close()
    end = time.time()
    _log(1, "Conversion took {0} seconds".format(end-start))
    return True


def main():
    parser = argparse.ArgumentParser(prog='convert.py', description='Parse command line parameters for converter.', add_help=False)
    parser.add_argument('-?', '--help', action='help', help='show this help message and exit')
    parser.add_argument('-s', '--source', default='smarthome.db', help='source database path, default is \'smarthome.db\'.')
    parser.add_argument('-e', '--engine', choices=['mysql', 'postgres'], default='mysql', help='destination database engine, default is \'mysql\'.')
    parser.add_argument('-h', '--host', default='localhost', help='destination database host, default is \'localhost\'.')
    parser.add_argument('-d', '--database', default='smarthome', help='destination database name, default is \'smarthome\'.')
    parser.add_argument('-ru', '--rootuser', default='root', help='destination database administrator username, default is \'root\'.')
    parser.add_argument('-rp', '--rootpassword')
    parser.add_argument('-u', '--user', default='smarthome', help='destination database smarthome username, default is \'smarthome\'.')
    parser.add_argument('-p', '--password', default='smarthome', help='destination database smarthome username, default is \'smarthome\'.')

    args = parser.parse_args()
    #_log(0, args)

    if not os.path.isfile(args.source):
        _log(3, "SQLite3 database {0} not found".format(args.source))
        return False
    # Prompt user for confirmation before doing anything
    answer = input("Are you sure you want to run conversion to {0} database '{1}'. CAUTION: DESTINATION DATABASE WILL BE OVERWRITTEN !! Enter (y)es or (n)o: ".format(args.engine, args.database))
    if answer != "yes" and answer != "y":
        return

    if args.engine == 'mysql' and tmysql:
        if(_convert_mysql(args)):
            _log(1, "")
            _log(1, "-----")
            _log(1, "Conversion successfull, use the following syntax in your plugin.conf:")
            _log(1, "")
            _log(1, "[database]")
            _log(1, "    class_path = plugins.database")
            _log(1, "    engine = mysql")
            _log(1, "    database = {0}".format(args.database))
            _log(1, "    host = {0}".format(args.host))
            _log(1, "    username = {0}".format(args.user))
            _log(1, "    password = {0}".format(args.password))
            _log(1, "")
        else:
            _log(3, "Conversion failed !")
    elif args.engine == 'postgres' and tpostgres:
        if(_convert_postgres(args)):
            _log(1, "")
            _log(1, "-----")
            _log(1, "Conversion successfull, use the following syntax in your plugin.conf:")
            _log(1, "")
            _log(1, "[database]")
            _log(1, "    class_path = plugins.database")
            _log(1, "    engine = postgres")
            _log(1, "    database = {0}".format(args.database))
            _log(1, "    host = {0}".format(args.host))
            _log(1, "    username = {0}".format(args.user))
            _log(1, "    password = {0}".format(args.password))
            _log(1, "")
        else:
            _log(3, "Conversion failed !")

    return

if __name__ == "__main__":
    main()
