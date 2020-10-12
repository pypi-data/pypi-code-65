import pymysql.cursors
import logging
import sys
from basacommons.SingletonMeta import SingletonMeta

class Database(metaclass = SingletonMeta):

    def __init__(self, config):
        self.host               = config.get('ddbb','host')
        self.port               = config.getint('ddbb','port')
        self.dbname             = config.get('ddbb','name')
        self.username           = config.get('ddbb','username')
        self.password           = config.get('ddbb','password')
        self.allow_management   = config.getboolean('ddbb','allow_management', fallback = False)
        self.conn               = None

    def open_connection(self):
        try:
            if self.conn is None:
                self.conn = pymysql.connect(self.host,
                                            port=self.port,    
                                            user=self.username,
                                            passwd=self.password,
                                            db=self.dbname,
                                            connect_timeout=5,
                                            charset = 'utf8mb4',
                                            cursorclass = pymysql.cursors.DictCursor)
        except pymysql.MySQLError as e:
            logging.error(e)
            sys.exit()
        finally:
            logging.debug('Connection opened successfully.')

    def run_query(self, query, args = None, page = None):
        self.__checkQueryIsAllowed(query)
        """Execute SQL query."""
        try:
            self.open_connection()
            with self.conn.cursor() as cur:
                if query.upper().startswith('SELECT'):
                    records = []
                    query = query + self.__pageToQuery(page)
                    cur.execute(query, args)
                    result = cur.fetchall()
                    for row in result:
                        records.append(row)
                    cur.close()
                    return records
                else:
                    result = cur.execute(query, args)
                    self.conn.commit()
                    affected = f"{cur.rowcount} rows affected."
                    cur.close()
                    return affected
        except pymysql.MySQLError as e:
            logging.error(e)
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
                logging.debug('Database connection closed.')            

    def __checkQueryIsAllowed(self, query):
        if self.allow_management:
            return
        if not (query.upper().startswith('SELECT') or query.upper().startswith('UPDATE') or query.upper().startswith('INSERT') or query.upper().startswith('DELETE')):
            logging.warning('Query \''+query+'\' is not allowed in non-management mode. To allow management mode, set coniguration value ddbb.allow_management = True')
            raise Exception(f'Query \'{query}\' is not allowed in non-management mode. To allow management mode, set coniguration value ddbb.allow_management = True')

    def __pageToQuery(self, page):
        if not page:
            return ''
        result = ''
        if page.sort_field:
            result = result + f' ORDER BY {page.sort_field} '
            if not page.sort_order_asc:
                result = result + ' DESC '
        if page.page_size:
            result = result + f' LIMIT {int(page.page_size)} '
            if page.page_number > 0:
                result = result + f' OFFSET {int(page.page_size * page.page_number)} '
        return result    

class Page:
    '''
    Utiltity class to handle pagination in SELECT queries.

    Attributes:
        page_number: (Optional) 0 index page number to be retrieved.
        page_size: (Optional) number of elements to be retrieved.
        page_field: (Optional) sorting field
        page_sort_asc: (Optional) defult:true. 
    '''
    def __init__(self,  page_size = None, page_number = 0, sort_field = None, sort_order_asc = True):
        assert page_number >= 0, 'Page number should be a non-negative integer'
        assert not page_size   or page_size >= 1, 'Page size should be a positive integer'
        self.page_number = page_number
        self.page_size = page_size
        self.sort_field = sort_field
        self.sort_order_asc = sort_order_asc
