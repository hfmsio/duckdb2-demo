import duckdb
from data import insert_sql, tickets
from ui import act, say, show


def run(ctx):
    act(2, "Triggers", "A row trigger writes an audit row per ticket. A statement trigger counts the rows in each batch.")
    con = duckdb.connect(ctx["db"])
    show(con, """CREATE TABLE inbox(id INT, payload VARCHAR); CREATE TABLE batches(n BIGINT);
                 CREATE TABLE audit(ticket INT, what VARCHAR)""")
    show(con, "CREATE TRIGGER log_new AFTER INSERT ON tickets FOR EACH ROW INSERT INTO audit VALUES (NEW.id, 'created')")
    show(con, """CREATE TRIGGER count_batches AFTER INSERT ON inbox REFERENCING NEW TABLE AS added FOR EACH STATEMENT
                 INSERT INTO batches SELECT count(*) FROM added""")
    say("New tickets land in the inbox. One statement moves the new ones into tickets.")
    con.execute(insert_sql("inbox", tickets(5, start=61)))
    show(con, "INSERT INTO tickets SELECT id, unnest(parse_ticket(payload)) FROM inbox WHERE id NOT IN (SELECT id FROM tickets)")
    show(con, "SELECT * FROM audit", rows=4)
    show(con, "SELECT * FROM batches")
    con.close()
