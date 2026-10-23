"""DuckLake 1.1: lakehouse tables with snapshots and time travel."""
import os
from lib import section, show


def run(con, work):
    section("DUCKLAKE")
    show(con, "INSTALL ducklake; LOAD ducklake")
    show(con, f"ATTACH 'ducklake:{work}/meta.ducklake' AS lake (DATA_PATH '{work}/lake_data/')")
    show(con, "CREATE TABLE lake.t AS SELECT i AS id FROM range(3) r(i)")
    show(con, "INSERT INTO lake.t VALUES (100)")
    show(con, "SELECT count(*) FROM lake.t", "now")
    show(con, "SELECT count(*) FROM lake.t AT (VERSION => 1)", "time travel to the first snapshot")
    show(con, "SELECT snapshot_id, changes FROM lake.snapshots()")
