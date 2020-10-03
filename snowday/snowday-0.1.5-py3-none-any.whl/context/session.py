from snowday.context.base import ContextFunction


# Session Context

CURRENT_ACCOUNT = ContextFunction(name="current_account")

CURRENT_ROLE = ContextFunction(name="current_role")

CURRENT_SESSION = ContextFunction(name="current_session")

CURRENT_STATEMENT = ContextFunction(name="current_statement")

CURRENT_TRANSACTION = ContextFunction(name="current_transaction")

CURRENT_USER = ContextFunction(name="current_user")

LAST_QUERY_ID = ContextFunction(name="last_query_id")

LAST_TRANSACTION = ContextFunction(name="last_transaction")


# Session Object Context

CURRENT_DATABASE = ContextFunction(name="current_database")

CURRENT_SCHEMA = ContextFunction(name="current_schema")

CURRENT_SCHEMAS = ContextFunction(name="current_schemas")

CURRENT_WAREHOUSE = ContextFunction(name="current_warehouse")

INVOKER_ROLE = ContextFunction(name="invoker_role")

INVOKER_SHARE = ContextFunction(name="invoker_share")

IS_GRANTED_TO_INVOKER_ROLE = ContextFunction(name="is_granted_to_invoker_role")

IS_ROLE_IN_SESSION = ContextFunction("is_role_in_session")
