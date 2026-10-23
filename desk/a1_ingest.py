import duckdb
from data import tickets
from ui import act, say, show


def run(ctx):
    act(1, "Ingest JSON", "Infer a schema from raw JSON text, patch the types, build a typed table. Keep the raw text as VARIANT.")
    con = duckdb.connect(ctx["db"])
    con.execute("CREATE TABLE raw(id INT, payload VARCHAR)")
    con.executemany("INSERT INTO raw VALUES (?, ?)", tickets(60))
    show(con, "SELECT id, left(payload, 70) AS payload FROM raw", rows=2)
    say("Infer one shape from every row, then fix only the types we care about.")
    shape = con.execute("""SELECT json_merge_patch(json_group_structure(payload::JSON),
        '{"ts":"TIMESTAMP","customer":{"id":"INTEGER"}}') FROM raw""").fetchone()[0]
    con.execute(f"CREATE MACRO parse_ticket(p) AS json_transform(p, '{shape}')")
    show(con, "CREATE TABLE tickets AS SELECT id, unnest(parse_ticket(payload)) FROM raw")
    show(con, "SELECT id, ts::VARCHAR AS ts, customer.name, product, resolved FROM tickets ORDER BY id", rows=3)
    say("Keep the raw text too, as VARIANT: stored as typed pieces, queried with dots.")
    show(con, "CREATE TABLE events AS SELECT id, payload::JSON::VARIANT AS v FROM raw")
    show(con, "SELECT v.customer.plan::VARCHAR AS plan, count(*) AS n FROM events GROUP BY 1 ORDER BY 2 DESC")
    con.close()
