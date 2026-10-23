import subprocess, sys, threading, time
import duckdb
from data import insert_sql, tickets
from ui import act, say, show

TOKEN = "desk-token"
SERVER = "import duckdb,time;c=duckdb.connect({db!r});c.execute('LOAD quack');c.execute(\"CALL quack_serve(token='{t}')\");time.sleep(120)"


def attach(con):
    for _ in range(40):
        try:
            return con.execute(f"ATTACH 'quack:localhost' AS qk (TOKEN '{TOKEN}')")
        except duckdb.Error:
            time.sleep(0.3)


def run(ctx):
    act(3, "Quack server", "Serve the database over the network. Three clients append at once, then a fourth connects and queries.")
    srv = subprocess.Popen([sys.executable, "-I", "-c", SERVER.format(db=ctx["db"], t=TOKEN)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        def worker(w):
            c = duckdb.connect(); c.execute("LOAD quack"); attach(c)
            c.execute(insert_sql("qk.inbox", tickets(10, start=100 + w * 10, seed=w)))
        say("Starting the server. Three intake workers send 10 tickets each.")
        ts = [threading.Thread(target=worker, args=(w,)) for w in range(3)]
        [t.start() for t in ts]; [t.join() for t in ts]
        dash = duckdb.connect(); dash.execute("LOAD quack"); attach(dash)
        say("The dashboard connects and every query runs on the server.")
        show(dash, "CONNECT qk")
        show(dash, "SELECT count(*) AS waiting FROM inbox")
        show(dash, "SELECT n AS tickets_in_batch, count(*) AS batches FROM batches GROUP BY 1")
        show(dash, "DISCONNECT")
    finally:
        srv.terminate(); srv.wait()
    con = duckdb.connect(ctx["db"])
    show(con, "INSERT INTO tickets SELECT id, unnest(parse_ticket(payload)) FROM inbox WHERE id NOT IN (SELECT id FROM tickets)")
    show(con, "SELECT count(*) AS tickets, (SELECT count(*) FROM audit) AS audit_rows FROM tickets")
    con.close()
