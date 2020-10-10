# From original SQLNet code.
# Wonseok modified. 20180607

import records
import re
import xlrd
from babel.numbers import parse_decimal, NumberFormatError


schema_re = re.compile(r'\((.+)\)') # group (.......) dfdf (.... )group
num_re = re.compile(r'[-+]?\d*\.\d+|\d+') # ? zero or one time appear of preceding character, * zero or several time appear of preceding character.
# Catch something like -34.34, .4543,
# | is 'or'

agg_ops = ['', 'MAX', 'MIN', 'COUNT', 'SUM', 'AVG']
cond_ops = ['=', '>', '<', 'OP']

class DBEngine:

    def __init__(self, fdb):
        #fdb = 'data/test.db'
        self.db = records.Database('sqlite:///{}'.format(fdb)).get_connection()
        self.data = xlrd.open_workbook('well_data_1.xls')
        self.table = self.data.sheet_by_name('data')
        self.data_row = self.table.row_values(0, 0)
        #print(self.data_row)
        self.dic = {}
        for i, x in enumerate(self.data_row):
            index = "col{}".format(i)
            self.dic[index] = x


    def execute_query(self, table_id, query, *args, **kwargs):
        return self.execute(table_id, query.sel_index, query.agg_index, query.conditions, *args, **kwargs)

    def execute(self, table_id, select_index, aggregation_index, conditions, lower=True):
        if not table_id.startswith('table'):
            table_id = 'table_{}'.format(table_id.replace('-', '_'))
        #table_info = self.db.query('SELECT sql from sqlite_master WHERE tbl_name = :name', name=table_id).all()[0].sql.replace('\n','')
        #schema_str = schema_re.findall(table_info)[0]
        schema_str = "col0 varchar(32), col1 varchar(32), col2 varchar(32), col3 varchar(32), col4 varchar(32), col5 varchar(80), col6 varchar(20), col7 varchar(60), col8 varchar(200), " \
      "col9 varchar(20), col10 varchar(60), col11 varchar(60), col12 varchar(60), col13 varchar(40), col14 varchar(20), col15 varchar(1), col16 varchar(32), col17 varchar(1), col18 varchar(80)," \
      " col19 varchar(200), col20 float, col21 varchar(100), col22 INTEGER, col23 varchar(20), col24 varchar(32), col25 varchar(30), col26 varchar(32), col27 varchar(20)," \
      " col28 varchar(64), col29 varchar(32), col30 varchar(20), col31 varchar(32), col32 varchar(20), col33 varchar(60), col34 varchar(60), col35 varchar(32), col36 varchar(32)," \
      " col37 float, col38 float, col39 float, col40 varchar(1), col41 varchar(1), col42 varchar(1), col43 INTEGER, col44 varchar(30), col45 float, col46 float, col47 varchar(20)," \
      " col48 float, col49 float, col50 float, col51 varchar(60), col52 float, col53 float, col54 float, col55 float, col56 float, col57 float, col58 INTEGER, col59 float, col60 varchar(10)," \
      " col61 varchar(20), col62 varchar(60), col63 varchar(60)"
        schema = {}
        for tup in schema_str.split(', '):
            t = tup.split()[1]
            c = tup.split()[0]
            schema[c] = t
        #print(schema)
        select_1 = 'col{}'.format(select_index)
        #print(select_1)
        #print(self.dic)
        select = self.dic[select_1]
        #print(select)
        agg = agg_ops[aggregation_index]
        if agg:
            select = '{}({})'.format(agg, select)
        where_clause = []
        where_map = {}
        #print("conditions=",conditions)

        for col_index, op, val in conditions:
            #print("conditions = ",conditions)
            #print(col_index,op,val)
            if lower and (isinstance(val, str) or isinstance(val, str)):
                val = val.lower()
            if schema['col{}'.format(col_index)] == 'real' and not isinstance(val, (int, float)):
                try:
                    # print('!!!!!!value of val is: ', val, 'type is: ', type(val))
                    # val = float(parse_decimal(val)) # somehow it generates error.
                    val = float(parse_decimal(val, locale='en_US'))
                    # print('!!!!!!After: val', val)

                except NumberFormatError as e:
                    try:
                        val = float(num_re.findall(val)[0]) # need to understand and debug this part.
                    except:
                        # Although column is of number, selected one is not number. Do nothing in this case.
                        pass
            # print(self.dic)
            where_clause.append('{} {} {}'.format(self.dic['col%d'%(col_index)], cond_ops[op], '\''+val+'\''))
            # print("col_index = ",col_index)
            # print("cond_ops[op] = ", cond_ops[op])
            # print("col_index = ", col_index)
            where_map['col{}'.format(col_index)] = val
            # print("where_map = ",where_map)
            # print("where_clause = ",where_clause)
        where_str = ''
        #print("where_clause=",where_clause)
        if where_clause:
            where_str = ' WHERE ' + ' AND '.join(where_clause)
            #where_str = " WHERE %s = \'%s\'"%(select,conditions[0][2])
        #print("where_str=", where_str)
        #print(select, table_id, where_str)
        query = 'SELECT {} AS result FROM {}{}'.format(select, table_id, where_str)
        #print(query)
        #print query
        out = self.db.query(query, **where_map)
        #print(out)
        #print('--------------------------')

        return [o.result for o in out]
    def execute_return_query(self, table_id, select_index, aggregation_index, conditions, lower=True):
        if not table_id.startswith('table'):
            table_id = 'table_{}'.format(table_id.replace('-', '_'))
        table_info = self.db.query('SELECT sql from sqlite_master WHERE tbl_name = :name', name=table_id).all()[0].sql.replace('\n','')
        schema_str = schema_re.findall(table_info)[0]
        schema = {}
        for tup in schema_str.split(', '):
            c, t = tup.split()
            schema[c] = t
        select = 'col{}'.format(select_index)
        agg = agg_ops[aggregation_index]
        if agg:
            select = '{}({})'.format(agg, select)
        where_clause = []
        where_map = {}
        for col_index, op, val in conditions:
            if lower and (isinstance(val, str) or isinstance(val, str)):
                val = val.lower()
            if schema['col{}'.format(col_index)] == 'real' and not isinstance(val, (int, float)):
                try:
                    # print('!!!!!!value of val is: ', val, 'type is: ', type(val))
                    # val = float(parse_decimal(val)) # somehow it generates error.
                    val = float(parse_decimal(val, locale='en_US'))
                    # print('!!!!!!After: val', val)

                except NumberFormatError as e:
                    val = float(num_re.findall(val)[0])
            where_clause.append('col{} {} :col{}'.format(col_index, cond_ops[op], col_index))
            where_map['col{}'.format(col_index)] = val
        where_str = ''
        if where_clause:
            where_str = 'WHERE ' + ' AND '.join(where_clause)
        query = 'SELECT {} AS result FROM {} {}'.format(select, table_id, where_str)
        #print query
        out = self.db.query(query, **where_map)


        return [o.result for o in out], query
    def show_table(self, table_id):
        if not table_id.startswith('table'):
            table_id = 'table_{}'.format(table_id.replace('-', '_'))
        rows = self.db.query('select * from ' +table_id)
        print(rows.dataset)