import duckdb
from common.ui import act, say, show


def run(ctx):
    act(7, "Snapshots", "DuckLake keeps one snapshot per load. AT (VERSION => n) reads the table as of an earlier load.")
    con = duckdb.connect()
    show(con, "INSTALL ducklake; LOAD ducklake")
    show(con, f"ATTACH '{ctx['work']}/desk.duckdb' AS desk (READ_ONLY)")
    show(con, f"ATTACH 'ducklake:{ctx['work']}/lake.ducklake' AS lake (DATA_PATH '{ctx['work']}/lake/')")
    show(con, "CREATE TABLE lake.open_by_product(day DATE, product VARCHAR, open_tickets BIGINT)")
    for day in ("2026-10-19", "2026-10-20", "2026-10-21"):
        con.execute(f"""INSERT INTO lake.open_by_product SELECT DATE '{day}', product, count(*) FROM desk.tickets
                        WHERE NOT resolved AND ts < DATE '{day}' + 1 GROUP BY product""")
    say("One snapshot per nightly load. Read the table as it was after the first one.")
    show(con, "SELECT product, open_tickets FROM lake.open_by_product AT (VERSION => 2) ORDER BY 1", rows=4)
    show(con, "SELECT sum(open_tickets) AS open_now FROM lake.open_by_product WHERE day = DATE '2026-10-21'")
    show(con, "SELECT snapshot_id, changes FROM lake.snapshots() ORDER BY 1", rows=4)
