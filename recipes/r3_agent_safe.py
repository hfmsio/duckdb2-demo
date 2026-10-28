import subprocess
import duckdb
from common.tools import cli_v2
from common.ui import recipe, say, show


def run(ctx):
    recipe(3, "Safe for AI agents", "Hide rows from an agent with a secure view, and see what its output looks like.")
    db = f"{ctx['work']}/agent.duckdb"
    con = duckdb.connect(db)
    show(con, """CREATE TABLE staff AS SELECT i AS id, 'person' || i AS name, ['eng', 'ops', 'exec'][1 + i % 3] AS dept,
                 CASE WHEN i % 3 = 2 THEN 500000 + i ELSE 50000 + i % 1000 END AS salary FROM range(3000) t(i)""")
    say("Executives are hidden by the view. A plain view still leaks them through column statistics.")
    show(con, "CREATE VIEW open_view AS SELECT id, name, dept, salary FROM staff WHERE dept <> 'exec'")
    show(con, "SELECT max(salary) AS real_max FROM open_view")
    show(con, "SELECT stats(salary) FROM open_view LIMIT 1", )
    say("A secure view gives back uninformative statistics and hides its query plan.")
    show(con, "CREATE SECURE VIEW agent_view AS SELECT id, name, dept, salary FROM staff WHERE dept <> 'exec'")
    show(con, "SELECT stats(salary) FROM agent_view LIMIT 1")
    visible = con.execute("SELECT count(*) FROM agent_view").fetchone()[0]
    con.close()
    exe = cli_v2()
    if not exe:
        return print("\n  skipped the agent part: needs the DuckDB 2.0 CLI (set DUCKDB_CLI).")
    say("Now the agent asks for everything. The CLI caps what it prints and adds a row count.")
    out = subprocess.run([exe, "-agent", "-readonly", db, "-c", "SELECT * FROM agent_view"], capture_output=True, text=True, timeout=30)
    lines = [l for l in (out.stdout + out.stderr).splitlines() if l.strip() and "duckdbrc" not in l and "agent mode on" not in l]
    for l in lines[:6] + ["    ..."] + lines[-5:]:
        print("    " + l[:120])
    print(f"\n    {len(lines)} lines printed for {visible} visible rows")
