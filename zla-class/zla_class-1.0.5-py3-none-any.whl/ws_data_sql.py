from datetime import datetime
from zla_utilities import \
    utility as ut

def get_sql_1(partnolist):
    sql_1 = 'orders.partno in {}'
    sel_data = sql_1.format(ut.sel_insql(partnolist))
    return sel_data


def get_sql_2(customerlist):
    sql_1 = 'ws.customerid in {}'
    if customerlist is not None:
        cus_data = sql_1.format(ut.sel_insql(customerlist))
    else:
        cus_data = None
    return cus_data


def get_sql_3(mlist):
    sql_base = 'orders.del1stdate '
    if all(x is None for x in mlist):
        _sql = sql_base + '>= DATE_SUB(now(), INTERVAL 48 MONTH)'
    elif all(type(x) is str for x in mlist):
        _subsql = convertor_bothdate(mlist)
        _sql = sql_base + _subsql
    else:
        _subsql = convertor_singledate(mlist)
        _sql = sql_base + _subsql
    return _sql


def convertor_bothdate(dlist):
    _start = datetime.strptime(dlist[0], '%Y-%m-%d')
    _end = datetime.strptime(dlist[1], '%Y-%m-%d')
    if _start > _end:
        print('Not allow start_date less than end_date !!')
        _sub = 'between "x" and "y"'
    else:
        _sub = 'between "{}" and "{}"'.format(dlist[0], dlist[1])

    return _sub


def convertor_singledate(dlist):
    if dlist[0] is not None:
        _sub = '>= "{}"'.format(dlist[0])
    else:
        _sub = 'between DATE_SUB("{}", INTERVAL 48 MONTH) and "{}"'.format(dlist[1], dlist[1])
    return _sub


def merge_wherecondition(sql_sentense):
    _where = [' (' + _sen + ') ' for _sen in sql_sentense if _sen is not None]
    return "and".join(_where)


def finishing_sql(_where):
    _sql = """select orders.partno, ws.customerid, ws.shipto ,ws.sotype,ws.sorg,ws.distch, ws.orderdate, orders.del1stdate,sum(orders.qty) as qty
            from partssaleorder as ws inner join orderdetails as orders on ws.saleorder = orders.saleorder
            where"""
    _groupby = " group by orders.partno, ws.customerid, ws.shipto , ws.sotype, ws.sorg, ws.distch, ws.orderdate,orders.del1stdate"
    msql = _sql + _where + _groupby
    return msql