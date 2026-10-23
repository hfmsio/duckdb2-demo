"""CLI agent mode: compact tables and JSON errors for coding agents. Needs the 2.0 CLI."""
import os, re, shutil, subprocess
from lib import section


def cli(args):
    exe = os.environ.get("DUCKDB_CLI") or shutil.which("duckdb")
    out = subprocess.run([exe, *args], capture_output=True, text=True, timeout=30)
    return "\n".join(l for l in (out.stdout + out.stderr).splitlines() if "duckdb agent mode" not in l and "duckdbrc" not in l and l.strip() and not l.startswith("\x1b"))


def run():
    section("CLI AGENT MODE")
    exe = os.environ.get("DUCKDB_CLI") or shutil.which("duckdb")
    found = re.search(r"\bv(\d+)\.", subprocess.run([exe, "--version"], capture_output=True, text=True).stdout) if exe else None
    if not found or int(found.group(1)) < 2:
        return print("skipped: needs the DuckDB 2.0 CLI. Set DUCKDB_CLI to its path")
    q = "SELECT range AS a, range * 2 AS b FROM range(3)"
    print(f"\n> duckdb -no-agent -c \"{q}\"\n{cli(['-no-agent', '-c', q])}")
    print(f"\n> duckdb -agent -c \"{q}\"\n{cli(['-agent', '-c', q])}")
    print(f"\n> duckdb -agent -c \"SELECT * FROM nope\"   -- errors come back as JSON\n{cli(['-agent', '-c', 'SELECT * FROM nope'])}")
