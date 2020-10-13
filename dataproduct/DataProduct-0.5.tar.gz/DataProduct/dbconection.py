import pypyodbc
DATABASE_CONFIG ={
    'Driver': 'SQL Server',
    'Server': 'BDProductMSSQL.mssql.somee.com',
    'Database': 'BDProductMSSQL',
    'UID': 'rwkama60_SQLLogin_1',
    'Password': '7ch5noj95a'
    }
def getConnection():
     connection = pypyodbc.connect("Driver= {"+DATABASE_CONFIG["Driver"]+"} ;Server=" + DATABASE_CONFIG["Server"] + ";Database="+DATABASE_CONFIG["Database"] + ";uid=" +DATABASE_CONFIG["UID"] + ";pwd=" +DATABASE_CONFIG["Password"])
     return connection

