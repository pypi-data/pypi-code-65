import math

from sqlalchemy import text


class BaseReport:
    __order__ = dict()
    __table__ = None
    __alias__ = None
    _date_fields = None
    _instance = None

    def __new__(cls, db_session, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, db_session):
        stmt = """select * from {0} limit 1""".format(self.__table__)

        stmt = text(stmt)
        results = db_session.execute(stmt)
        columns = [k for k, v in dict(results.fetchone()).items()]

        self._columns = columns

    def filter(self, db_session, filter_, **filters):
        if filter_ not in self._columns:
            raise Exception

        filters.pop(filter_, None)

        where, params = self.where(**filters)
        where = where.replace("where ", "and ")

        stmt = """
        select distinct {0}
        from {1}
        where {0} is not null and {0}::text != '' {2}
        order by {0}
        """.format(filter_, self.__table__, where)

        stmt = text(stmt).bindparams(**params)

        results = db_session.execute(stmt)
        return [r[0] for r in results]

    def ordering(self, order_string):
        if order_string is None:
            return ""

        order_by = []
        ordering = order_string.split(";")

        for o in ordering:
            if ":" in o:
                key, dir_ = o.split(":")
            else:
                key, dir_ = o, None

            order, dir_default = self.__order__.get(key, (key, "desc"))
            dir_ = dir_ or dir_default
            if dir_ == "desc":
                dir_ = "desc nulls last"
            order_by.append(order + " " + dir_)

        return "order by " + ", ".join(order_by)

    def where(self, **filters):
        filter_ = "where 1 = 1"
        params = {}

        for key, value in filters.items():
            if key not in self._columns:
                continue
            filter_ += " and {0} = :{0}".format(key)
            params[key] = value

        for date_key in self._date_fields:
            date_from_key = "{}_from".format(date_key)
            date_to_key = "{}_to".format(date_key)

            if date_from_key in filters:
                filter_ += " and {0} >= :{0}_from".format(date_key)
                params[date_from_key] = filters[date_from_key]

            if date_to_key in filters:
                filter_ += " and {0} < :{0}_to".format(date_key)
                params[date_to_key] = filters[date_to_key]

        return filter_, params

    def report(self, db_session, order=None, per_page=10, page=1, **filters):
        stmt, params = self.statement(order=order, **filters)
        stmt = text(stmt).bindparams(
            limit=int(per_page),
            offset=int(per_page) * (int(page) - 1),
            **params,
        )

        results = db_session.execute(stmt)

        return [
            dict(s)
            for s in results
        ]

    def drill(self, db_session, **filters):
        stmt, params = self.drill_statement(**filters)
        stmt = text(stmt).bindparams(
            **params,
        )

        results = db_session.execute(stmt)

        return [
            dict(s)
            for s in results
        ]

    def pagination(self, db_session, order=None, per_page=10, page=1, **filters):
        stmt, params = self.total_statement(**filters)
        stmt = text(stmt).bindparams(**params)

        results = db_session.execute(stmt)
        total = results.first()[0]

        return {
            "page_count": math.ceil(total / int(per_page)),
            "item_count": total,
            "per_page": int(per_page),
            "page": int(page),
        }


class Field:
    def __init__(self, header, key, drill=None):
        self.header = header
        self.key = key
        self.drill = drill


class BaseRenderer:
    __alias__ = None
    title = None
    filters = None
    fields = None
    drill_fields = None

    @property
    def template_data(self):
        return {"title": self.title, "filters": self.filters, "fields": self.fields, "alias": self.__alias__}

    @property
    def drill_data(self):
        return {"title": self.title, "fields": self.drill_fields, "alias": self.__alias__}


class TraderRenderer(BaseRenderer):
    __alias__ = "trader"

    title = "Trader Stats"
    filters = ["asset", "year"]
    fields = [
        Field("Alias", "alias"),
        Field("Account Number", "account_number", lambda x: "?account_number={}".format(x["account_number"])),
        Field("Account Name", "account_name"),
        Field("Start Date", "start_date"),
        Field("Probability", "probability"),
        Field("Initial Balance", "initial_balance"),
        Field("Currency", "currency"),
        Field("Balance", "balance"),
        Field("Equity", "equity"),
        Field("Gain", "gain"),
        Field("PNL Pips", "pnl_pips"),
        Field("PNL Cash", "pnl_cash"),
        Field("Closed", "closed", lambda x: "?closed=1&account_number={}".format(x["account_number"])),
        Field("Closed Volume", "volume"),
        Field("Toxicity", "toxic_perc"),
    ]

    drill_fields = [
        Field("Alias", "alias"),
        Field("Account Number", "account_number"),
        Field("Account Name", "account_name"),
        Field("PNL Cash", "pnl_cash"),
    ]


class TraderReport(BaseReport):
    __alias__ = "trader"
    __table__ = "trader_stats"
    __order__ = {
        "gain": ("pnl_cash / nullif(coalesce(b.opening_balance, a.initial_balance), 0)", "desc"),
        "opening_balance": ("coalesce(b.opening_balance, a.initial_balance)", "desc"),
        "alias": ("a.alias", "asc"),
        "account_number": ("a.account_number", "asc"),
        "account_name": ("a.account_name", "asc"),
    }

    _date_fields = ["date"]

    def drill_statement(self, **filters):
        where, params = self.where(**filters)
        where = where.replace("account_number = ", "s.account_number = ")
        stmt = """
            select
                s.*,
                a.alias,
                a.account_name
            from trader_stats s
            join account a
            on a.account_number = s.account_number
            {0}
        """.format(where)
        return stmt, params

    def statement(self, order="", **filters):
        balance_filter = "where opened = 0"
        if filters.get("date_from"):
            balance_filter += " and date < :date_from"
        else:
            balance_filter += " and 1 = 0"

        stats_where, params = self.where(**filters)
        stats_where = stats_where.replace("where 1 = 1", "where initial != true")

        order_by = self.ordering(order)

        stmt = """
            select
                trunc(pnl_cash / nullif(coalesce(b.opening_balance, a.initial_balance), 0) * 100, 2) as gain,
                coalesce(b.opening_balance, a.initial_balance) as opening_balance,
                s.*,
                a.*
            from account a
            join (
                select
                    sum(win) as win,
                    sum(loss) as loss,
                    sum(buy) as buy,
                    sum(sell) as sell,
                    sum(opened) as opened,
                    sum(closed) as closed,
                    trunc(sum(win)::decimal / nullif(sum(closed), 0) * 100, 2) as probability,
                    trunc(sum(toxic)::decimal / nullif(sum(closed), 0) * 100, 2) as toxic_perc,
                    trunc(sum(tp_hit)::decimal / nullif(sum(closed), 0) * 100, 2) as tp_hit_perc,
                    trunc(sum(sl_hit)::decimal / nullif(sum(closed), 0) * 100, 2) as sl_hit_perc,
                    trunc(sum(
                        case
                            when win = 1 then pnl_cash
                            else 0
                        end
                    ) / nullif(sum(closed), 0), 2) as win_pnl_cash_avg,
                    trunc(sum(
                        case
                            when win = 1 then pnl_pips
                            else 0
                        end
                    ) / nullif(sum(closed), 0), 2) as win_pnl_pips_avg,
                    trunc(sum(
                        case
                            when loss = 1 then pnl_cash
                            else 0
                        end
                    ) / nullif(sum(closed), 0), 2) as loss_pnl_cash_avg,
                    sum(
                        case
                            when closed = 1 then pnl_cash
                            else 0
                        end
                    ) pnl_cash,
                    sum(
                        case
                            when closed = 1 then pnl_pips
                            else 0
                        end
                    ) pnl_pips,
                    sum(
                        case
                            when opened = 1 then pnl_cash
                            else 0
                        end
                    ) open_pnl_cash,
                    sum(
                        case
                            when opened = 1 then pnl_pips
                            else 0
                        end
                    ) open_pnl_pips,
                    sum(volume) as volume,
                    sum(deposit) as deposit,
                    sum(withdrawl) as withdrawal,
                    account_number
                from trader_stats
                {0}
                group by account_number
            ) s on s.account_number = a.account_number
            left join (
                select
                    account_number,
                    sum(pnl_cash) + sum(deposit) + sum(withdrawl) as opening_balance
                from trader_stats
                {1}
                group by account_number
            ) b on b.account_number = a.account_number
            {2}
            limit :limit
            offset :offset
        """.format(stats_where, balance_filter, order_by)
        return stmt, params

    def total_statement(self, **filters):
        stats_where, params = self.where(**filters)
        stats_where = stats_where.replace("where 1 = 1", "where initial != true")

        stmt = """
            select count(distinct(account_number))
            from trader_stats
            {0}
        """.format(stats_where)

        return stmt, params
