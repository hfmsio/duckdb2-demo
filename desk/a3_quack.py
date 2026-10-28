import threading
import duckdb
from common.tools import quack_client, quack_server
from common.ui import act, say, show
from data import insert_sql, tickets


def run(ctx):
    act(3, "Quack server", "Serve the database over the network. Three clients append at once, then a fourth connects and queries.")
    with quack_server(ctx["db"]):
        def worker(w):
            quack_client().execute(insert_sql("qk.inbox", tickets(10, start=100 + w * 10, seed=w)))
        say("Starting the server. Three intake workers send 10 tickets each.")
        ts = [threading.Thread(target=worker, args=(w,)) for w in range(3)]
        [t.start() for t in ts]; [t.join() for t in ts]
        dash = quack_client()
        say("The dashboard connects and every query runs on the server.")
        show(dash, "CONNECT qk")
        show(dash, "SELECT count(*) AS waiting FROM inbox")
        show(dash, "SELECT n AS tickets_in_batch, count(*) AS batches FROM batches GROUP BY 1")
        show(dash, "DISCONNECT")
    con = duckdb.connect(ctx["db"])
    show(con, "INSERT INTO tickets SELECT id, unnest(parse_ticket(payload)) FROM inbox WHERE id NOT IN (SELECT id FROM tickets)")
    show(con, "SELECT count(*) AS tickets, (SELECT count(*) FROM audit) AS audit_rows FROM tickets")
    con.close()
