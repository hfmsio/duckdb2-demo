"""Extensible parser: the DuckPGQ community extension adds graph syntax (SQL/PGQ)."""
import duckdb
from lib import section, show


def run():
    section("EXTENSIBLE PARSER (DuckPGQ)")
    con = duckdb.connect()
    show(con, "INSTALL duckpgq FROM community; LOAD duckpgq")
    show(con, "CREATE PROPERTY GRAPH g VERTEX TABLES (p)", "before opting in: plain SQL does not know this")
    show(con, "SET active_grammar_extensions = ['duckpgq']", "opt in to the extension's grammar")
    show(con, """CREATE TABLE p AS SELECT * FROM (VALUES (1, 'Ann'), (2, 'Bo'), (3, 'Cy')) t(id, name);
                 CREATE TABLE k AS SELECT * FROM (VALUES (1, 2), (2, 3)) t(a, b)""")
    show(con, """CREATE PROPERTY GRAPH g VERTEX TABLES (p)
                 EDGE TABLES (k SOURCE KEY (a) REFERENCES p (id) DESTINATION KEY (b) REFERENCES p (id) LABEL knows)""")
    show(con, """SELECT * FROM GRAPH_TABLE (g MATCH (x:p)-[e:knows]->(y:p) COLUMNS (x.name AS src, y.name AS dst))""",
         "graph pattern as SQL")
    show(con, """SELECT * FROM GRAPH_TABLE (g MATCH q = ANY SHORTEST (x:p)-[e:knows]->{1,3}(y:p)
                 COLUMNS (x.name AS src, y.name AS dst, path_length(q) AS hops)) ORDER BY hops, src""",
         "shortest paths, 1 to 3 hops")
