# skeema
MySQL/MariaDB/Percona data analysis tool.

## License
AGPLv3

## Author
8c30ff1057d69a6a6f6dc2212d8ec25196c542acb8620eb4148318a4b10dd131

## Features
* Generates unique MD5 sum for a database.
* Generates unique MD5 sum for tables.
* Get the engine for every table in a database.
* Get the size of a table (in MB) for a database.
* Get the size of the database.
* Get total rows per table for a database.
* Scans a database for foreign key issues (InnoDB only).

## Installation
* Clone and run `skeema`

## Switches
* `-u <username>` specifies the user to use when connecting to mariadb.
* `-p <password>` specifies the password to use when connecting to mariadb.
* `-s <socket>` specifies the full path to the socket to use when connecting to mariadb.
* `-d` prints the database schema md5 sum.
* `-t` prints the table schemas and their md5 sum.
* `-e` prints the engines for each table.
* `-S` prints the size of each table.
* `-D` prints the size of the database.
* `-c` prints the row count of each table.
* `-F` prints any foreign key issues that are detected.

## Examples
* `skeema -u root -p root -s /var/run/mysqld/mysqld.sock -S -D mysql` outputs the size of each table and the size of the database.
* `skeema -u root -p root -s /var/run/mysqld/mysqld.sock -t mysql` outputs the unique schema all tables in specified database.
* `skeema -u root -p root -s /var/run/mysqld/mysqld.sock -F blah` scans the blah database for foreign key issues.
