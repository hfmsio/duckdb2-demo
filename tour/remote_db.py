"""CONNECT to PostgreSQL: the session runs on the server. Needs Docker; starts and removes a throwaway container."""
import shutil, subprocess, time
import duckdb
from lib import section, show

PORT, DSN = 55432, "dbname=mydb host=127.0.0.1 port=55432 user=postgres password=demo"


def run():
    section("CONNECT to PostgreSQL")
    if not shutil.which("docker"):
        return print("skipped: needs docker")
    subprocess.run(["docker", "run", "-d", "--rm", "--name", "duckdb2-demo-pg", "-e", "POSTGRES_PASSWORD=demo",
                    "-e", "POSTGRES_DB=mydb", "-p", f"{PORT}:5432", "postgres:16"], capture_output=True, check=True)
    try:
        con = duckdb.connect()
        show(con, "INSTALL postgres; LOAD postgres")
        for _ in range(60):
            try:
                con.execute(f"ATTACH '{DSN}' AS pg (TYPE postgres)")
                break
            except duckdb.Error:
                time.sleep(1)
        show(con, "CREATE TABLE pg.orders AS SELECT i AS id, i % 5 AS cust, i * 1.5 AS amt FROM range(100000) t(i)")
        show(con, f"CONNECT 'postgres:{DSN}'", "from here, plain SQL runs on PostgreSQL")
        show(con, "SELECT cust, count(*), sum(amt) FROM orders GROUP BY cust ORDER BY cust", "aggregated by the server")
        show(con, "EXPLAIN SELECT cust FROM orders", "known gap: EXPLAIN is wrapped in COPY and PostgreSQL rejects it")
        show(con, "DISCONNECT")
    finally:
        subprocess.run(["docker", "stop", "duckdb2-demo-pg"], capture_output=True)
