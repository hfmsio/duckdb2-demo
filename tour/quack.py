"""Quack: DuckDB as a network server, plus CONNECT."""
import subprocess, sys, threading, time
import duckdb
from lib import section, show

TOKEN = "demo-token"
SERVER = f"""
import duckdb, time
c = duckdb.connect(); c.execute("LOAD quack")
c.execute("CREATE TABLE sales AS SELECT i AS id, i * 10 AS amt FROM range(1000) r(i)")
c.execute("CREATE TABLE ev(w INT, i INT); CREATE TABLE ctr(id INT PRIMARY KEY, n INT); INSERT INTO ctr VALUES (1, 0)")
c.execute("CALL quack_serve(token='{TOKEN}')")
time.sleep(60)
"""


def run(con):
    section("QUACK server + CONNECT")
    srv = subprocess.Popen([sys.executable, "-I", "-c", SERVER], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        show(con, "LOAD quack")
        for _ in range(30):
            try:
                con.execute(f"ATTACH 'quack:localhost' AS qk (TOKEN '{TOKEN}')")
                break
            except duckdb.Error:
                time.sleep(0.3)
        show(con, "SELECT count(*), sum(amt) FROM qk.sales", "query the remote table by name")
        show(con, "CONNECT qk", "session now runs on the server")
        show(con, "SELECT count(*), max(amt) FROM sales", "plain SQL, executed remotely")
        show(con, "DISCONNECT")
        writes()
    finally:
        srv.kill()


def client():
    c = duckdb.connect()
    c.execute("LOAD quack")
    c.execute(f"ATTACH 'quack:localhost' AS qk (TOKEN '{TOKEN}')")
    return c


def parallel(fn, workers=8):
    ts = [threading.Thread(target=fn, args=(w,)) for w in range(workers)]
    [t.start() for t in ts]
    [t.join() for t in ts]


def writes(workers=8, n=100):
    section("QUACK concurrent writes")
    lost = []

    def append(w):
        c = client()
        for i in range(n):
            c.execute(f"INSERT INTO qk.ev VALUES ({w}, {i})")

    def bump(w, retry):
        c = client()
        for _ in range(n // 4):
            while True:
                try:
                    c.execute("UPDATE qk.ctr SET n = n + 1 WHERE id = 1")
                    break
                except duckdb.TransactionException:
                    lost.append(1)
                    if not retry:
                        break

    probe = client()
    parallel(append, workers)
    got = probe.execute("SELECT count(*) FROM qk.ev").fetchone()[0]
    print(f"\n  appends: {workers} clients x {n} rows -> {got} of {workers * n} landed")

    for retry in (False, True):
        probe.execute("UPDATE qk.ctr SET n = 0")
        lost.clear()
        parallel(lambda w: bump(w, retry), workers)
        got = probe.execute("SELECT n FROM qk.ctr").fetchone()[0]
        print(f"  same-row updates, retry={retry}: counter {got} of {workers * (n // 4)}, conflicts hit {len(lost)}")
