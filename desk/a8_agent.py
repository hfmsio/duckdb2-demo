import subprocess
from common.tools import cli_v2
from common.ui import act, say


def cli(exe, db, sql):
    out = subprocess.run([exe, "-agent", "-readonly", db, "-c", sql], capture_output=True, text=True, timeout=30)
    keep = [l for l in (out.stdout + out.stderr).splitlines() if l.strip() and "duckdbrc" not in l and "agent mode on" not in l]
    return "\n".join("    " + l[:160] for l in keep)


def run(ctx):
    act(8, "CLI agent mode", "The 2.0 CLI detects a coding agent and answers in markdown tables and JSON errors.")
    exe = cli_v2()
    if not exe:
        return print("\n  skipped: needs the DuckDB 2.0 CLI. Set DUCKDB_CLI to its path (see README).")
    for sql in ("SELECT product, count(*) AS open FROM tickets WHERE NOT resolved GROUP BY 1 ORDER BY 2 DESC",
                "SELECT cstomer FROM tickets"):
        say(sql if "cstomer" not in sql else sql + "   (a typo, on purpose)")
        print(cli(exe, ctx["db"], sql))
