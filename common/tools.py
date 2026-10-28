"""Shared helpers: the 2.0 CLI, and a Quack server with its client connect step."""
import contextlib, os, re, shutil, subprocess, sys, time
import duckdb

TOKEN = "demo-token"
SERVER = "import duckdb,time;c=duckdb.connect({db!r});c.execute('LOAD quack');c.execute(\"CALL quack_serve(token='{t}')\");time.sleep(300)"


def cli_v2():
    """Path of a DuckDB 2.x CLI from DUCKDB_CLI or PATH, else None."""
    exe = os.environ.get("DUCKDB_CLI") or shutil.which("duckdb")
    found = re.search(r"\bv(\d+)\.", subprocess.run([exe, "--version"], capture_output=True, text=True).stdout) if exe else None
    return exe if found and int(found.group(1)) >= 2 else None


@contextlib.contextmanager
def quack_server(db):
    """Serve a database file over Quack until the block ends."""
    srv = subprocess.Popen([sys.executable, "-I", "-c", SERVER.format(db=db, t=TOKEN)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        yield
    finally:
        srv.terminate()
        srv.wait()


def quack_client():
    """A new connection attached to the local Quack server as 'qk'."""
    con = duckdb.connect()
    con.execute("LOAD quack")
    for _ in range(40):
        try:
            con.execute(f"ATTACH 'quack:localhost' AS qk (TOKEN '{TOKEN}')")
            return con
        except duckdb.Error:
            time.sleep(0.3)
    raise RuntimeError("Quack server did not start")
