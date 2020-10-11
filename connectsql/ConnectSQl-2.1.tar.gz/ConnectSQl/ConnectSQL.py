""" Create and access SQL functions very easily..."""


import mysql.connector as sql


class ConnectSql(object):
    """ ConnectSQL is a very useful & perfectly designed module to Connect to SQL database & retrieve data."""
    def __init__(self, Username, Password):
        """ Initialize some values before Starting.
        Parameters:
            Username: Enter Your Username.
            Password: Enter your Password.
        By default host is Local Host as per your machine's IP Address.
        Recommendation:
            We Recommend setting the default value of the table which will help you in skipping parameters.
            Method: <Object>.default_table(self).
            """
        self.user = Username
        self.password = Password
        self.mycon = sql.connect(host='localhost', user=self.user, password=self.password, database='class_xii')
        self.cur = self.mycon.cursor()
        self.true = False
        self.table = None

    def create_db(self, dbname):
        """ Create Database Method.
        Parameters:
            dbname: Name of the database.
        Just type name of the database & Create it.
        Its Simple. Isn't it ?
        """
        try:
            self.cur.execute('Create Database {}'.format(dbname))
            self.mycon.commit()
            print(f'\nQuery Ok, {dbname} Successfully Created.')
        except sql.Error:
            raise ConnectionError(f'Database{dbname} Exists or Check Syntax')

    def show_db(self):
        """ This methods helps you show all the database stored in your Machine."""
        self.cur.execute("show databases")
        data = self.cur.fetchall()
        print('\nFollowing are the databases: ')
        for i in range(len(data)):
            for j in range(len(data[i])):
                print(f'\t DB{i + 1}: {data[i][j]}')
        print(f'{self.cur.rowcount} row(s) in a set.')

    def use(self, database):
        """Use the required Database.
        AS per SQL Syntax use database clause is necessary.
        This method helps you in using the database.
        Parameters:
            database: Name of database to be set.
        """
        try:
            self.cur.execute("use %s" % database)
            print(f'\nDatabase Changed.')
        except sql.Error:
            raise ConnectionError('Invalid Database Name')

    def show_tables(self):
        """ Shows all the tables after in a Given database."""
        self.cur.execute("show tables")
        data1 = self.cur.fetchall()
        print(f'Tables are: ')
        for i in range(len(data1)):
            for j in range(len(data1[i])):
                print(f'\t {i + 1}: {data1[i][j]}')
        print(f'{self.cur.rowcount} row(s) in a set.')

    def create_table(self, query):
        """ Create a table within Minutes.
        Parameters:
            query: Type the complete query required for creating a database.
        """
        self.cur.execute(query)
        print('\nQuery Ok, 0 row(s) affected.')

    def insert_values(self, values, columns=None, table=None):
        """
        This Method insert values in the table.
        Parameters:
             table: Name of the Table
                    default is None (Applicable only when you set default value for table).
             values: Use Single Query String for Values Parameter.
             columns: Columns must be set of all logical columns in the table.
        """
        try:
            if self.true:
                table = self.table

            if columns is None:
                query = "Insert into {} values ({})".format(table, values)
                self.cur.execute(query)
            else:
                query = "Insert into {}({}) values{}".format(table, columns, values)
                self.cur.execute(query)
            self.mycon.commit()
            print(f'\nQuery Ok, {self.cur.rowcount} row(s) affected.')
        except sql.Error:
            raise ConnectionError('Check SQL SYNTAX')

    def select(self, query, table=None):
        """ Select & Retrieve data from Mysql.
        Parameters:
            query: Type the complete query as per your needs.
            table: Name of the Table
                   default is None (Applicable only when you set default value for table).
        """
        if self.table:
            table=self.table
        self.cur.execute(query)
        data = self.cur.fetchall()
        nor = self.cur.rowcount
        self.show_result(data, table=table)
        print(f'\nQuery Ok, {len(data)} row(s) in a set.')

    def desc(self, table=None):
        """ Describe a table.
        Parameters:
            table: Name of the Table
                    default is None (Applicable only when you set default value for table).
        """
        if self.true:
            table = self.table
        self.cur.execute("Desc {}".format(table))
        data = self.cur.fetchall()
        self.show_result(data, table=table)
        print(f'{self.cur.rowcount} row(s) in a set.')

    def delete(self, query=None, complete=None):
        """ Delete any rows.
        Parameters:
            query: Type the complete query required for deleting from a database.
            complete: Delete all records from a database.
                      default is None (Applicable only when you set default value for table).
        """
        try:
            if self.true:
                complete = self.table
            if complete is not None:
                self.cur.execute('delete from {}'.format(complete))
                print(f'\nQuery Ok, {self.cur.rowcount} row(s) affected.')
            else:
                self.cur.execute(query)
                print(f'\nQuery Ok, {self.cur.rowcount} row(s) affected.')
            self.mycon.commit()
        except sql.Error:
            raise ConnectionError('Check SQL Syntax.')

    def alter(self, table=None, modify=None, change=None, add_column=None, add_key=None, drop_column=None,
              drop_key=None):
        """ Alter the Table.
        Parameters:
            table: Name of the Table
                    default is None (Applicable only when you set default value for table).
            modify: Modify the table.
                    Do not type the complete Query.
                    Just type in required format after modify clause as per SQL syntax.
            change: Change the name/Positions of the table.
                    Do not type the complete Query.
                    Just type in required format after change clause as per SQL syntax.
            add_column: Add a column to your Database.
                        Do not type the complete Query.
                        Just type in required format after Add clause as per SQL syntax.
            add_key: Add a key to the database.
                     Do not type the complete Query.
                     Just type in required format after Add clause as per SQL syntax.
            drop_column: Drop a Column from any Database.
                         Do not type the complete Query.
                         Just type in required format after modify clause as per SQL syntax.
                         Do not type Column keyword, We'll do it for you.
            drop_key: Drop a key from any table.
                      Do not type the complete Query.
                      Just type in required format after modify clause as per SQL syntax.
                      Do not type Key keyword, We'll do it for you.
        """
        if self.true:
            table = self.table
        if modify is not None:
            self.cur.execute('Alter Table {} modify {}'.format(table, modify))
        if change is not None:
            self.cur.execute('Alter Table {} change {}'.format(table, change))
        if add_column is not None:
            self.cur.execute('Alter Table {} Add {}'.format(table, add_column))
        if add_key is not None:
            self.cur.execute('Alter Table {} Add {}'.format(table, add_key))
        if drop_column is not None:
            self.cur.execute('Alter Table {} Drop Column {}'.format(table, drop_column))
        if drop_key is not None:
            self.cur.execute('Alter Table {} Drop {} key'.format(table, drop_key))
        self.mycon.commit()
        print(f'\nQuery Ok {self.cur.rowcount} row(s) affected.')

    def drop(self, table=None, column=None, key=None):
        """ Another alternative for dropping keys etc. from Table.
        Parameters:
            table: Name of the Table
                   default is None (Applicable only when you set default value for table).
            column: Just write the name of the Column to be dropped.
            key: Just write the name of key to be Dropped.
        """
        if self.true:
            table = self.table
        if column is not None:
            self.cur.execute('Alter Table {} Drop Column {}'.format(table, column))
        if key is not None:
            self.cur.execute('Alter Table {} Drop {} key'.format(table, key))
        else:
            self.cur.execute('Drop Table {}'.format(table))
        self.mycon.commit()
        print(f'\nQuery Ok {self.cur.rowcount} row(s) affected.')

    def update(self, set, where, table=None):
        """ Update the values in a table.
        Parameters:
            table: Name of the Table
                   default is None (Applicable only when you set default value for table).
            set: Conditions for Set Clause.
                 Type as per SQL Syntax.
            where: Conditions after where clause.
                   Type as per SQL Syntax.
        """
        if self.true:
            table = self.table
        self.cur.execute('Update {} set {} where {}'.format(table, set, where))
        self.mycon.commit()
        print(f'\nQuery Ok {self.cur.rowcount} row(s) affected.')

    def default_table(self, table):
        """ Most Exclusive.
        Parameters:
            table: Set the default value for table.
                   This will help you in skipping Parameters.
                   We Recommend this Method before starting to work.
        """
        self.true = True
        self.table = table

    def disp_table(self, table=None):
        """ Display All Records of a table.
        Parameters:
            table: Name of the Table
                   default is None (Applicable only when you set default value for table).
        """
        if self.true:
            table = self.table
        self.cur.execute('select *from {}'.format(table))
        data = self.cur.fetchall()
        self.show_result(data, table=table)
        print(f'{self.cur.rowcount} row(s) in a set.')

    def query(self, query, table=None):
        """For Complex Queries use this Method.
        Parameters:
            query: Type the Complete Query to retrieve data.
            table: Name of the Table
                   default is None (Applicable only when you set default value for table).
        """
        if self.true:
            table = self.table
        self.cur.execute(query)
        data = self.cur.fetchall()
        nor =self.cur.rowcount
        self.show_result(data, table=table)
        print(f'\nQuery Ok, {nor} row(s) in a set.')

    def show_result(self, data, table=None):
        """ Not for Users. Only for Developers."""
        print(f'\nFollowing Results Were obtained:')
        if self.table:
            table = self.table
        self.cur.execute("desc {}".format(table))
        data1 = self.cur.fetchall()
        c = [column[0] for column in data1]
        print(f'\t C:  {c}')
        for i in range(len(data)):
            print(f"\t R{i + 1}: {data[i]}")




