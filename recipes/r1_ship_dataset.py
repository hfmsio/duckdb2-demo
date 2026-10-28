import os
import duckdb
from common.ui import recipe, say, show


def run(ctx):
    recipe(1, "Ship a dataset as one tiny file", "Publish Parquet files through a small read-only catalog anyone can attach.")
    data, cat = f"{ctx['work']}/events", f"{ctx['work']}/events_catalog.duckdb"
    con = duckdb.connect()
    say("2,000,000 events with a VARIANT payload, written as Parquet into europe/ and americas/ folders, sorted by day.")
    show(con, f"""COPY (SELECT i AS id, DATE '2024-01-01' + (i % 1000)::INT AS day, ['de', 'fr', 'us'][1 + i % 3] AS country,
                 ('{{"device":"' || ['ios', 'web'][1 + i % 2] || '","ms":' || (i % 500) || '}}')::JSON::VARIANT AS payload
                 FROM range(2000000) t(i)) TO '{data}' (FORMAT parquet, PARTITION_BY (country), ORDER_BY (day),
                 PARTITION_PATH CASE WHEN country = 'us' THEN 'americas/' || country ELSE 'europe/' || country END)""")
    print("   ", sorted({os.path.relpath(r, data) for r, _, fs in os.walk(data) if fs}))
    say("The catalog holds only the query text. Consumers attach it and see ordinary tables.")
    cat_con = duckdb.connect(cat)
    cat_con.execute(f"""CREATE VIEW events AS SELECT * EXCLUDE (filename), regexp_extract(filename, '/([a-z]{{2}})/data_', 1) AS country
                        FROM read_parquet('{data}/**/*.parquet', filename = true);
                        CREATE VIEW slow_by_device AS SELECT payload.device::VARCHAR AS device, count(*) AS slow
                        FROM events WHERE payload.ms::INT > 400 GROUP BY 1""")
    cat_con.close()
    mb = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(data) for f in fs) / 1e6
    print(f"\n    data: {mb:.1f} MB of Parquet, catalog file: {os.path.getsize(cat) // 1024} KB")
    reader = duckdb.connect()
    show(reader, f"ATTACH '{cat}' AS shop (READ_ONLY)")
    show(reader, "SELECT device, slow FROM shop.slow_by_device ORDER BY device")
    show(reader, "SELECT country, count(*) AS events FROM shop.events GROUP BY 1 ORDER BY 1")
    show(reader, "CREATE VIEW shop.mine AS SELECT 1", "readers cannot change the shared catalog")
