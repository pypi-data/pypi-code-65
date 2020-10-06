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
        stmt = """
            select column_name
            from information_schema.columns
            where table_name = :table_name
        """

        stmt = text(stmt).bindparams(table_name=self.__table__)
        results = db_session.execute(stmt)
        columns = [r[0] for r in results]

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
