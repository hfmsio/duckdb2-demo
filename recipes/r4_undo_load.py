import duckdb
from common.ui import recipe, say, show


def run(ctx):
    recipe(4, "Undo a bad data load", "DuckLake snapshots let you read a table as it was before a bad batch.")
    w = ctx["work"]
    con = duckdb.connect()
    show(con, "INSTALL ducklake; LOAD ducklake")
    show(con, f"ATTACH 'ducklake:{w}/books.ducklake' AS lake (DATA_PATH '{w}/books/')")
    show(con, "CREATE TABLE lake.orders(id INT, amount DOUBLE)")
    show(con, "INSERT INTO lake.orders SELECT i, 10 + i FROM range(100) t(i)", )
    say("A second load arrives with a broken exporter: negative amounts.")
    show(con, "INSERT INTO lake.orders SELECT 100 + i, -1 FROM range(50) t(i)")
    show(con, "SELECT count(*) AS rows, count(*) FILTER (WHERE amount < 0) AS bad FROM lake.orders")
    show(con, "SELECT snapshot_id, changes FROM lake.snapshots() ORDER BY 1", rows=5)
    say("Read the table as it was after the first load, and restore it.")
    show(con, "SELECT count(*) AS rows, count(*) FILTER (WHERE amount < 0) AS bad FROM lake.orders AT (VERSION => 2)")
    show(con, "CREATE OR REPLACE TABLE lake.orders AS SELECT * FROM lake.orders AT (VERSION => 2)")
    show(con, "SELECT count(*) AS rows, count(*) FILTER (WHERE amount < 0) AS bad FROM lake.orders")
