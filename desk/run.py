"""Support desk on DuckDB 2.0, one story. Usage: python desk/run.py [act number ...]"""
import importlib, os, sys, tempfile
sys.path[:0] = [os.path.dirname(__file__), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]

ACTS = ["a1_ingest", "a2_triggers", "a3_quack", "a4_similar", "a5_graph", "a6_ai", "a7_timetravel", "a8_agent"]


def main(only):
    import duckdb
    print(f"Support desk on DuckDB {duckdb.__version__}")
    with tempfile.TemporaryDirectory() as work:
        ctx = {"work": work, "db": f"{work}/desk.duckdb"}
        for n, name in enumerate(ACTS, 1):
            if not only or str(n) in only:
                importlib.import_module(name).run(ctx)


if __name__ == "__main__":
    main(sys.argv[1:])
