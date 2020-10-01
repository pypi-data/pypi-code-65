from datasette import hookimpl
from datasette.utils.asgi import Response, NotFound, Forbidden
from urllib.parse import quote_plus
import sqlite_utils


@hookimpl
def permission_allowed(actor, action):
    if action == "edit-schema" and actor and actor.get("id") == "root":
        return True


@hookimpl
def register_routes():
    return [
        (r"^/-/edit-schema$", edit_schema_index),
        (r"^/-/edit-schema/(?P<database>[^/]+)$", edit_schema_database),
        (r"^/-/edit-schema/(?P<database>[^/]+)/(?P<table>[^/]+)$", edit_schema_table),
    ]


TYPES = {
    str: "TEXT",
    float: "REAL",
    int: "INTEGER",
    bytes: "BLOB",
}
REV_TYPES = {v: k for k, v in TYPES.items()}


def get_databases(datasette):
    return [db for db in datasette.databases.values() if db.is_mutable]


async def check_permissions(datasette, request):
    if not await datasette.permission_allowed(
        request.actor, "edit-schema", default=False
    ):
        raise Forbidden("Permission denied for edit-schema")


async def edit_schema_index(datasette, request):
    await check_permissions(datasette, request)
    databases = get_databases(datasette)
    if 1 == len(databases):
        return Response.redirect(
            "/-/edit-schema/{}".format(quote_plus(databases[0].name))
        )
    return Response.html(
        await datasette.render_template(
            "edit_schema_index.html", {"databases": databases}, request=request
        )
    )


async def edit_schema_database(request, datasette):
    await check_permissions(datasette, request)
    databases = get_databases(datasette)
    database_name = request.url_vars["database"]
    just_these_tables = set(request.args.getlist("table"))
    try:
        database = [db for db in databases if db.name == database_name][0]
    except IndexError:
        raise NotFound("Database not found")
    tables = []
    hidden_tables = set(await database.hidden_table_names())
    for table_name in await database.table_names():
        if just_these_tables and table_name not in just_these_tables:
            continue
        if table_name in hidden_tables:
            continue

        def get_columns(conn):
            return [
                {"name": column, "type": dtype}
                for column, dtype in sqlite_utils.Database(conn)[
                    table_name
                ].columns_dict.items()
            ]

        columns = await database.execute_write_fn(get_columns, block=True)
        tables.append({"name": table_name, "columns": columns})
    return Response.html(
        await datasette.render_template(
            "edit_schema_database.html",
            {
                "database": database,
                "tables": tables,
            },
            request=request,
        )
    )


async def edit_schema_table(request, datasette):
    await check_permissions(datasette, request)
    table = request.url_vars["table"]
    databases = get_databases(datasette)
    database_name = request.url_vars["database"]
    try:
        database = [db for db in databases if db.name == database_name][0]
    except IndexError:
        raise NotFound("Database not found")
    if not await database.table_exists(table):
        raise NotFound("Table not found")

    if request.method == "POST":
        formdata = await request.post_vars()
        if formdata.get("action") == "update_columns":
            types = {}
            rename = {}
            drop = set()
            order_pairs = []

            def get_columns(conn):
                return [
                    {"name": column, "type": dtype}
                    for column, dtype in sqlite_utils.Database(conn)[
                        table
                    ].columns_dict.items()
                ]

            existing_columns = await database.execute_fn(get_columns)

            for column_details in existing_columns:
                column = column_details["name"]
                new_name = formdata.get("name.{}".format(column))
                if new_name and new_name != column:
                    rename[column] = new_name
                if formdata.get("delete.{}".format(column)):
                    drop.add(column)
                types[column] = (
                    REV_TYPES.get(formdata.get("type.{}".format(column)))
                    or column_details["type"]
                )
                order_pairs.append((column, formdata.get("sort.{}".format(column), 0)))

            order_pairs.sort(key=lambda p: int(p[1]))

            def transform_the_table(conn):
                sqlite_utils.Database(conn)[table].transform(
                    types=types,
                    rename=rename,
                    drop=drop,
                    column_order=[p[0] for p in order_pairs],
                )

            await database.execute_write_fn(transform_the_table, block=True)

            datasette.add_message(request, "Changes to table have been saved")

            return Response.redirect(request.path)

        if "delete_table" in formdata:
            return await delete_table(request, datasette, database, table)
        elif "add_column" in formdata:
            return await add_column(request, datasette, database, table, formdata)
        else:
            return Response.html("Unknown operation", status=400)

    def get_columns_and_schema(conn):
        t = sqlite_utils.Database(conn)[table]
        columns = [
            {"name": column, "type": dtype} for column, dtype in t.columns_dict.items()
        ]
        return columns, t.schema

    columns, schema = await database.execute_fn(get_columns_and_schema)

    columns_display = [
        {
            "name": c["name"],
            "type": TYPES[c["type"]],
        }
        for c in columns
    ]

    return Response.html(
        await datasette.render_template(
            "edit_schema_table.html",
            {
                "database": database,
                "table": table,
                "columns": columns_display,
                "schema": schema,
                "types": list(TYPES.values()),
            },
            request=request,
        )
    )


async def delete_table(request, datasette, database, table):
    def do_delete_table(conn):
        db = sqlite_utils.Database(conn)
        db[table].disable_fts()
        db[table].drop()
        db.vacuum()

    await datasette.databases[database.name].execute_write_fn(
        do_delete_table, block=True
    )
    datasette.add_message(request, "Table has been deleted")
    return Response.redirect("/-/edit-schema/" + database.name)


async def add_column(request, datasette, database, table, formdata):
    name = formdata["name"]
    type = formdata["type"]

    def do_add_column(conn):
        db = sqlite_utils.Database(conn)
        db[table].add_column(name, type)

    await datasette.databases[database.name].execute_write_fn(do_add_column, block=True)

    return Response.redirect(
        "/{}/{}".format(quote_plus(database.name), quote_plus(table))
    )
