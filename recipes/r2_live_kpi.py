import threading, time
import duckdb
from common.tools import quack_client, quack_server
from common.ui import recipe, say, show


def run(ctx):
    recipe(2, "Live KPI counter shared by many dashboards", "A trigger records every batch. Writers append over Quack and dashboards read the totals.")
    db = f"{ctx['work']}/kpi.duckdb"
    con = duckdb.connect(db)
    show(con, "CREATE TABLE orders(id INT, amount DOUBLE); CREATE TABLE kpi_log(orders BIGINT, revenue DOUBLE)")
    show(con, """CREATE TRIGGER roll_up AFTER INSERT ON orders REFERENCING NEW TABLE AS added FOR EACH STATEMENT
                 INSERT INTO kpi_log SELECT count(*), sum(amount) FROM added""")
    show(con, "CREATE VIEW kpi AS SELECT sum(orders)::BIGINT AS orders, round(sum(revenue), 2) AS revenue FROM kpi_log")
    say("The trigger only appends, so writers never fight over one counter row.")
    con.close()
    seen = []
    with quack_server(db):
        ready = threading.Barrier(7)

        def write(w):
            c = quack_client()
            ready.wait()
            for b in range(5):
                time.sleep(0.15)
                rows = ", ".join(f"({w * 1000 + b * 100 + i}, {10 + i % 7})" for i in range(20))
                c.execute(f"INSERT INTO qk.orders VALUES {rows}")

        done = threading.Event()

        def read(_):
            c = quack_client()
            mine = []
            ready.wait()
            while not done.is_set():
                mine.append(c.execute("SELECT coalesce(orders, 0) FROM qk.kpi").fetchone()[0])
                time.sleep(0.05)
            mine.append(c.execute("SELECT coalesce(orders, 0) FROM qk.kpi").fetchone()[0])
            seen.append(mine)
        say("Four writers add 5 batches of 20 orders each while three dashboards keep reading.")
        readers = [threading.Thread(target=read, args=(i,)) for i in range(3)]
        writers = [threading.Thread(target=write, args=(w,)) for w in range(4)]
        [t.start() for t in readers + writers]; [t.join() for t in writers]; done.set(); [t.join() for t in readers]
        final = quack_client()
        show(final, "SELECT * FROM qk.kpi", )
        show(final, "SELECT count(*) AS batches FROM qk.kpi_log")
    check = duckdb.connect(db, read_only=True)
    show(check, "SELECT count(*) AS orders, round(sum(amount), 2) AS revenue FROM orders", )
    for i, mine in enumerate(seen, 1):
        print(f"\n    dashboard {i}: {len(mine)} reads, orders went {mine[0]} to {mine[-1]}, never went backwards: {mine == sorted(mine)}")
