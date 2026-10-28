"""Four use cases on DuckDB 2.0. Usage: python recipes/run.py [number ...]"""
import importlib, os, sys, tempfile
sys.path[:0] = [os.path.dirname(__file__), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]

RECIPES = ["r1_ship_dataset", "r2_live_kpi", "r3_agent_safe", "r4_undo_load"]


def main(only):
    import duckdb
    print(f"Recipes on DuckDB {duckdb.__version__}")
    with tempfile.TemporaryDirectory() as work:
        for n, name in enumerate(RECIPES, 1):
            if not only or str(n) in only:
                importlib.import_module(name).run({"work": work})


if __name__ == "__main__":
    main(sys.argv[1:])
