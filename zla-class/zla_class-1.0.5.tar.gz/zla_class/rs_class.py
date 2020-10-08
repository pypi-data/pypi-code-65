from .master_sql import *
from .rs_data_sql import *
from .rs_method import *
from zla_general import \
    vendor_finding_bymat as vmat, \
    header_ecnbysap_bymat as ecnmat

class get_rs(object):
    def __init__(self, partno, start=None, end=None, customer=None, parent=False):
        """
        For getting SKC retail data as your requirment
        :param partno: part number is needed.
        :param start: start date (option)
        :param end: end date (option)
        :param customer: customer code by sap only (option)
        :param parent: if True data will be get all of branch data together (default is False)
        """
        # Make character sentense
        self.partno = partno
        self.allcustomer = customer_parentable(customer, parent)
        self.dictchain = ecnmat.get_chaindictionary(partno)
        self.master = get_partsmaster(partno)
        self.character = get_partscharacter(partno)
        self.purchasing = get_partspurchasing(partno)
        self.vendor, self.cost, self.mapping = vmat.get_vendor_mat(partno, self.purchasing.get('spt'))

        # Make sql_sentense
        sql_frntpartno, sql_servpartno = get_sql_1(self.dictchain.keys())
        sql_frntcustomer, sql_servcustomer = get_sql_2(self.allcustomer)
        sql_frnttimerange, sql_servtimerange = get_sql_3([start, end])
        list_frntsql = [sql_frntpartno, sql_frntcustomer, sql_frnttimerange]
        list_servsql = [sql_servpartno, sql_servcustomer, sql_servtimerange]
        where_frntsql = merge_wherecondition(list_frntsql)
        where_servsql = merge_wherecondition(list_servsql)
        frnt_msql,serv_msql = finishing_sql(where_frntsql,where_servsql)
        self.frntdata = History(get_data(frnt_msql))
        self.servdata = History(get_data(serv_msql))
        self.rsdata = History(merge_data(self.frntdata.raw,self.servdata.raw))


class History(pd.DataFrame):
    def __init__(self,_data):
        super(History, self).__init__()
        self.raw = _data

    def history(self,_by='days'):
        """
        generate SKC retails sale data as your requirement
        :param _by:
        - 'days'(default) is shown for dialy data
        - 'weeks' is shown for weekly data
        - 'months' is shown for monthly data
        - 'years' is shown for annual data}
        :return:
        Dataframe with date index
        """
        return to_number(self.raw,_by)
