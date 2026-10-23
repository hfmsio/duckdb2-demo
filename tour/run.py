"""DuckDB 2.0 feature tour. Usage: python tour/run.py [section ...]  (sql variant triggers quack lakes catalog grammar json small typed_ai agent storage; remote needs docker, runs only when named)"""
import sys, tempfile
import duckdb
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import agent_cli, catalog, grammar, json_typed, lakes, quack, remote_db, small, sql_features, triggers, typed_ai, variant
from lib import section, show


def storage(con, work):
    section("STORAGE FORMAT")
    path = f"{work}/v2.duckdb"
    show(con, f"ATTACH '{path}' AS v2; CREATE TABLE v2.t AS SELECT 1 AS x")
    show(con, "SELECT database_name, path FROM duckdb_databases() WHERE database_name = 'v2'")
    print("\n  Files written by 2.0 cannot be opened by DuckDB 1.x (it reports a newer file version).")


def main(only):
    with tempfile.TemporaryDirectory() as work:
        con = duckdb.connect()
        print(f"DuckDB {duckdb.__version__}")
        steps = {
            "sql": lambda: sql_features.run(con),
            "variant": lambda: variant.run(con, work),
            "triggers": lambda: triggers.run(con),
            "quack": lambda: quack.run(duckdb.connect()),
            "lakes": lambda: lakes.run(duckdb.connect(), work),
            "catalog": lambda: catalog.run(work),
            "grammar": grammar.run,
            "json": lambda: json_typed.run(con),
            "small": lambda: small.run(con),
            "typed_ai": typed_ai.run,
            "agent": agent_cli.run,
            "storage": lambda: storage(con, work),
            "remote": remote_db.run,
        }
        for name, step in steps.items():
            if name in only or (not only and name != 'remote'):
                step()


if __name__ == "__main__":
    main(sys.argv[1:])
