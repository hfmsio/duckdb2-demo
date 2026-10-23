import duckdb
from ui import act, say, show


def run(ctx):
    act(4, "Similarity search", "A NEAREST join finds the closest solved ticket for each open ticket.")
    con = duckdb.connect(ctx["db"])
    say("A toy embedding: one number per keyword. A real one would come from a model.")
    show(con, """CREATE OR REPLACE MACRO embed(t) AS
                 list_transform(['refund', 'log', '503', 'wifi'], lambda k: contains(lower(t), k)::DOUBLE)::DOUBLE[4]""")
    show(con, """SELECT o.id, o.subject, s.id AS solved_id, s.resolution
                 FROM (SELECT * FROM tickets WHERE NOT resolved ORDER BY id LIMIT 3) o
                 INNER JOIN (SELECT * FROM tickets WHERE resolved) s
                   NEAREST 1 BY DISTANCE array_distance(embed(o.subject || ' ' || o.body), embed(s.subject || ' ' || s.body))
                 ORDER BY o.id""", rows=3)
    con.close()
