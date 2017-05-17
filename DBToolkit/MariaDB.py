import MySQLdb
import hashlib
import re
import sys


class MariaDB:
    database = ""
    username = ""
    password = ""
    host     = ""
    socket   = "/var/lib/mysql/mysql.sock"

    dbconn = None
    dbcur  = None

    tables          = []
    tableengines    = None
    tablesizesraw   = None
    tablesizescount = None
    tablesums       = None
    databasesum     = None
    databasesize    = 0
    badforeignkeys  = []

    def __init__(self, database="test", username="root", password="", host="localhost", socket=""):
        self.database = database
        self.username = username
        self.password = password
        self.host     = host
        self.socket   = socket

        # initialize connection and cursor objects
        try:
            self.dbconn = MySQLdb.connect(host, username, password, database, unix_socket=socket)
            self.dbcur = self.dbconn.cursor()
        except MySQLdb.OperationalError as e:
            print("Code: %s\nMessage: %s" % (e[0], e[1]))
            sys.exit(1)

    # store all of a databases tables
    def gen_tables(self):
        self.dbcur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s", (self.database,))
        self.tables = [i[0] for i in self.dbcur.fetchall()]
        return self.tables

    # generate a checksum on SHOW CREATE TABLE <TABLE> and store in hash
    def table_sums(self):
        tablesums = dict()

        self.gen_tables()

        # generate md5 sums for each table in the database
        if len(self.tables) > 0:
            md5 = hashlib.md5()

            for table in self.tables:
                self.dbconn.query("SHOW CREATE TABLE %s" % table)
                results = self.dbconn.store_result()

                row = results.fetch_row(results.num_rows())[0]
                tableschema = re.sub('AUTO_INCREMENT=(X{5}|[0-9]{0,6})', 'AUTO_INCREMENT=XXXXX', row[1])
                md5.update(tableschema)
                tablesums[row[0]] = md5.hexdigest()

        self.tablesums = tablesums
        return(self.tablesums)

    # generates md5 sum based on the table sums
    def database_sum(self):
        self.table_sums()

        if len(self.tablesums) > 0:
            bigstr = ""

            for key in self.tablesums.iterkeys():
                bigstr = bigstr + self.tablesums[key]

            md5 = hashlib.md5()
            md5.update(bigstr)
            self.databasesum = {self.database: md5.hexdigest()}
            return self.databasesum

    # store a list of tables to engines
    def get_table_engines(self):
        self.dbcur.execute("SELECT TABLE_NAME,ENGINE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s", (self.database,))
        results = self.dbcur.fetchall()
        self.tableengines = dict(results)
        return self.tableengines

    # get table sizes
    def get_table_sizes(self):
        self.dbcur.execute("SELECT TABLE_NAME, ROUND( ( (data_length + index_length) / 1024 / 1024), 2) AS size FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s", (self.database,))
        results = self.dbcur.fetchall()
        self.tablesizesraw = dict(results)
        return self.tablesizesraw
    
    # get table row counts
    def get_table_row_size(self):
        self.dbcur.execute("SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=%s", (self.database,))
        results = self.dbcur.fetchall()
        self.tablesizescount = dict(results)
        return self.tablesizescount
    
    # get database size
    def database_size(self):
        self.get_table_sizes()

        dbsize = 0

        if len(self.tablesizesraw) > 0 or self.databasesize == 0:
            for key in self.tablesizesraw.iterkeys():
                dbsize = dbsize + self.tablesizesraw[key]
            
            self.databasesize = {self.database: dbsize}
        
        return(self.databasesize)
    
    # foreign key checker
    def check_foreign_keys(self):
        self.dbcur.execute("SELECT DISTINCT KEY_COLUMN_USAGE.CONSTRAINT_NAME, KEY_COLUMN_USAGE.TABLE_NAME, KEY_COLUMN_USAGE.COLUMN_NAME, KEY_COLUMN_USAGE.REFERENCED_TABLE_NAME, KEY_COLUMN_USAGE.REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ON TABLE_CONSTRAINTS.CONSTRAINT_NAME=KEY_COLUMN_USAGE.CONSTRAINT_NAME WHERE TABLE_CONSTRAINTS.CONSTRAINT_TYPE=\"FOREIGN KEY\" AND TABLE_CONSTRAINTS.CONSTRAINT_SCHEMA=%s", (self.database,))
        prep = self.dbcur.fetchall()
        
        # 0 = CONSTRAINT_NAME
        # 1 = TABLE_NAME
        # 2 = COLUMN_NAME
        # 3 = REFERENCED_TABLE_NAME
        # 4 = REFERENCED_COLUMN_NAME
        # 5 = DATABASE
        for row in prep:
            query = "SELECT {1}.{2} AS CHILD_ID, {3}.{4} AS PARENT_ID FROM {5}.{1} LEFT JOIN {5}.{3} ON {1}.{2}={3}.{4} WHERE {3}.{4} IS NULL".format(row[0], row[1], row[2], row[3], row[4], self.database)
            self.dbcur.execute(query)
            results = self.dbcur.fetchall()

            if len(results) > 0:
                for baddata in results:
                    bad_data = ({"CONSTRAINT_NAME": row[0], "TABLE_NAME": row[1], "COLUMN_NAME": row[2], "REFERENCED_TABLE_NAME": row[3], "REFERENCED_COLUMN_NAME": row[4], "CHILD_ID": baddata[0], "PARENT_ID": baddata[1], "DATABASE": self.database})
                    self.badforeignkeys.append(bad_data)
        
        return(self.badforeignkeys)
