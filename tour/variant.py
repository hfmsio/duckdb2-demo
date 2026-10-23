"""VARIANT: semi-structured data stored as typed, compressed pieces."""
import os
from lib import section, show


def run(con, work):
    section("VARIANT")
    show(con, """CREATE TABLE events AS SELECT i AS id,
                 ('{"user":"u' || (i % 3) || '","tags":["a","b"],"n":' || i || '}')::JSON::VARIANT AS v
                 FROM range(5) r(i)""")
    show(con, "SELECT typeof(v), variant_type(v), variant_keys(v) FROM events LIMIT 1")
    show(con, "SELECT v.user, v.tags[1], v.n FROM events ORDER BY id", "dot and index access")
    show(con, "SELECT variant_exists(v, 'user') FROM events LIMIT 1")
    path = os.path.join(work, "events.parquet")
    show(con, f"COPY events TO '{path}'", "written as shredded Parquet")
    show(con, f"SELECT count(*), sum(v.n::INT) FROM '{path}'", "read back, only needed fields")
