import os


class Member(object):
    
    def __init__(self, api_object):
        self._api_object = api_object

    def organization_id(self):
        return self._api_object["organization"]["id"]
    
    def snowflake_creds(self):
        username = self._api_object.get("snowUsername", "")
        password = self._api_object.get("snowPassword", "")
        org = self._api_object.get("organization", {})
        
        account=org.get("account", "")
        database=org.get("database", "")
        schema=org.get("schema", "")
        warehouse = org.get("warehouse", "")
        supplied_creds = {
            "username": username,
            "password": password,
            "account": account,
            "database": database,
            "schema": schema,
            "warehouse": warehouse,
        }

        if "user" not in supplied_creds and "username" in supplied_creds:
            # The Rasgo API supplies this value as "username", but the Snowflake API expects "user". 
            supplied_creds["user"] = supplied_creds["username"]
        
        default_creds = {
            "account": os.environ.get("SNOWFLAKE_ACCOUNT", "aya46528"),
            "database": os.environ.get("SNOWFLAKE_DATABASE", "RASGOALPHA"),
            "schema":  os.environ.get("SNOWFLAKE_SCHEMA", "public"),
            "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            }

        fields = ["account", "user", "password", "database", "schema", "warehouse", "role"]
        creds = dict([(f, supplied_creds.get(f, default_creds.get(f))) for f in fields])

        if creds["role"] is None:
            # If the Rasgo API does not supply a role, we infer it from their user name. We
            # need to do this after the fact because we need to determine what the user name
            # is before we can perform the inference.
            creds["role"] = creds["user"]  + "_role"

        # Allow environment variables to override Snowflake Credentials
        #creds['user'] = os.environ.get('SNOWFLAKE_USERNAME', creds['user'])
        #creds['password'] = os.environ.get('SNOWFLAKE_PASSWORD', creds['password'])
        #creds['role'] = os.environ.get('SNOWFLAKE_ROLE', creds['role'])
        
        return creds

        
