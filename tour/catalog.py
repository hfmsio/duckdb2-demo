"""A database with no data in it: a small file of views over Parquet, attached read-only."""
import os
import duckdb
from lib import section, show


def run(work):
    section("VIEW-ONLY CATALOG")
    data, cat = f"{work}/services.parquet", f"{work}/catalog.duckdb"
    con = duckdb.connect(cat)
    con.execute(f"COPY (SELECT i AS id, i % 3 AS line FROM range(30) t(i)) TO '{data}'")
    show(con, f"CREATE VIEW services AS SELECT * FROM '{data}'", "the file stores the query text, not rows")
    con.close()
    print(f"\n  catalog file: {os.path.getsize(cat) // 1024} KB, data file stays where it is")
    con = duckdb.connect()
    show(con, f"ATTACH '{cat}' AS rail (READ_ONLY)")
    show(con, "SELECT line, count(*) FROM rail.services GROUP BY line ORDER BY line", "queries run against the Parquet")
    show(con, "CREATE VIEW rail.x AS SELECT 1", "read-only: nobody edits the shared catalog")
