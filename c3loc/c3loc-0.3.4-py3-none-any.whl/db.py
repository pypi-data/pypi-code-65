import asyncpg

from .config import CONFIG


async def init_db_pool():
    db_url = f"postgres://{CONFIG['DB_USER']}:{CONFIG['DB_PASSWORD']}@{CONFIG['DB_HOST']}/{CONFIG['DB_NAME']}"
    db_url_redacted = f"postgres://{CONFIG['DB_USER']}:*****@{CONFIG['DB_HOST']}"
    print(f"Connecting to {db_url_redacted}")
    pool = await asyncpg.create_pool(dsn=db_url)
    return pool


async def init_db(pool, reset_db):
    tables = ['zones', 'tags', 'listener', 'log']
    async with pool.acquire() as connection:
        if reset_db:
            for table in tables:
                await connection.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
        async with connection.transaction():
            print('\tEnsuring schema')
            await connection.execute(DB_CREATE_STR)


DB_CREATE_STR = """
CREATE TABLE IF NOT EXISTS zones (
    id serial,
    name varchar,
    attrs jsonb,
    PRIMARY KEY(id));

CREATE TABLE IF NOT EXISTS groups (
    id serial,
    name varchar,
    attrs jsonb,
    PRIMARY KEY(id));

CREATE TABLE IF NOT EXISTS listeners (
    id varchar not null,
    name varchar,
    zone_id int,
    last_seen timestamp without time zone DEFAULT (now() at time zone 'utc'),
    attrs jsonb,
    PRIMARY KEY(id),
    UNIQUE(name),
    CONSTRAINT fk_zone
        FOREIGN KEY(zone_id)
        REFERENCES zones(id)
        ON DELETE SET NULL);

DO $$ BEGIN
    CREATE TYPE tag_type as ENUM ('iBeacon', 'SmartRelay', 'LocationAnchor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS tags (
    id serial,
    name varchar,
    mac macaddr,
    uuid uuid,
    major int4,
    minor int4,
    type tag_type NOT NULL,
    attrs jsonb,
    zone_id integer,
    last_seen timestamp without time zone DEFAULT (now() at time zone 'utc'),
    group_id integer,
    PRIMARY KEY (id),
    CONSTRAINT uk_ibeacon
    UNIQUE (uuid, major, minor),
    CONSTRAINT uk_mac
    UNIQUE (mac),
    CONSTRAINT fk_zone
                  FOREIGN KEY (zone_id)
                  REFERENCES zones(id)
                  ON DELETE SET NULL,
    CONSTRAINT fk_group
                  FOREIGN KEY (group_id)
                  REFERENCES groups(id)
                  ON DELETE SET NULL
);

CREATE OR REPLACE FUNCTION def_tag_name() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.name IS NOT NULL OR NEW.name != ''
       THEN RETURN NEW;
    ELSIF NEW.type = 'iBeacon' THEN
        NEW.name := 'iBeacon ' || NEW.uuid || ':' || NEW.major || ':' || NEW.minor;
    ELSIF NEW.type = 'LocationAnchor' THEN
            NEW.name := 'Location Anchor ' || NEW.major || ':' || NEW.minor;
    ELSIF NEW.type = 'SmartRelay' THEN
            NEW.name := 'SmartRelay ' || NEW.mac;
    END IF;
    return NEW;
END
$$;

DO $$ BEGIN
    CREATE TRIGGER tags_set_def_name
    BEFORE INSERT OR UPDATE ON tags
    FOR EACH ROW
    EXECUTE PROCEDURE def_tag_name();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE report_reason as ENUM ('ENTRY', 'MOVE', 'STATUS', 'EXIT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS log (
    tag_id int,
    zone_id int,
    ts timestamp without time zone default (now() at time zone 'utc'),
    distance_cm numeric(4,2),
    variance real,
    listener_id varchar,
    data jsonb,
    anchor_dist numeric(4,2),
    anchor_ts_delta int,
    anchor_id int,
    reason report_reason,
    CONSTRAINT fk_tag
                 FOREIGN KEY (tag_id)
                 REFERENCES tags(id)
                 ON DELETE CASCADE,
    CONSTRAINT fk_zone
                 FOREIGN KEY (zone_id)
                 REFERENCES zones(id)
                 ON DELETE SET NULL,
    CONSTRAINT fk_anchor
                 FOREIGN KEY (anchor_id)
                 REFERENCES tags(id)
                 ON DELETE SET NULL,
    CONSTRAINT fk_listener
                 FOREIGN KEY (listener_id)
                 REFERENCES listeners(id)
                 ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_log_tag_id ON log (tag_id);
CREATE INDEX IF NOT EXISTS idx_log_anchor_id ON log (anchor_id);
CREATE INDEX IF NOT EXISTS idx_log_zone_id ON log (zone_id);
CREATE INDEX IF NOT EXISTS idx_log_ts ON log (ts DESC);
"""
