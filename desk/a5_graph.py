import duckdb
from common.ui import act, say, show


def run(ctx):
    act(5, "Graph queries", "DuckPGQ adds property graphs and MATCH patterns through the extensible parser.")
    con = duckdb.connect(ctx["db"])
    show(con, "INSTALL duckpgq FROM community; LOAD duckpgq")
    show(con, "SET active_grammar_extensions = ['duckpgq']", )
    say("Customers open tickets. Every API outage ticket points at the first outage ticket.")
    show(con, """CREATE OR REPLACE TABLE customer AS SELECT DISTINCT customer.id AS id, customer.name AS name FROM tickets;
                 CREATE OR REPLACE TABLE opened AS SELECT customer.id AS cust, id AS ticket FROM tickets;
                 CREATE OR REPLACE TABLE dup AS SELECT id AS ticket, min(id) OVER () AS root
                   FROM tickets WHERE product = 'api' QUALIFY id > min(id) OVER ()""")
    show(con, """CREATE OR REPLACE PROPERTY GRAPH desk VERTEX TABLES (customer, tickets)
                 EDGE TABLES (opened SOURCE KEY (cust) REFERENCES customer (id) DESTINATION KEY (ticket) REFERENCES tickets (id),
                              dup SOURCE KEY (ticket) REFERENCES tickets (id) DESTINATION KEY (root) REFERENCES tickets (id))""")
    show(con, """SELECT * FROM GRAPH_TABLE (desk MATCH (c:customer)-[o:opened]->(t:tickets)-[d:dup]->(r:tickets)
                 COLUMNS (c.name AS customer, t.id AS ticket, r.id AS root_ticket)) ORDER BY ticket""", rows=4)
    con.close()
