"""New SQL surface in 2.0."""
from lib import section, show


def run(con):
    section("SQL: lambdas, variables, FETCH FIRST")
    show(con, "SELECT list_transform([1,2,3], x -> x + 1)", "old arrow syntax: now an error")
    show(con, "SELECT list_transform([1,2,3], lambda x: x + 1)", "new syntax")
    show(con, "SET VARIABLE limit_n = 2")
    show(con, "SELECT * FROM range(10) FETCH FIRST $limit_n ROWS ONLY", "$var shorthand + SQL-standard FETCH")

    section("SQL: nested schemas, MERGE, data-modifying CTEs")
    show(con, "CREATE SCHEMA finance; CREATE SCHEMA finance.reports")
    show(con, "CREATE TABLE finance.reports.q3(k INT, v INT); INSERT INTO finance.reports.q3 VALUES (1, 10)")
    show(con, """MERGE INTO finance.reports.q3 t USING (VALUES (1, 99), (2, 5)) n(k, v) ON t.k = n.k
                 WHEN MATCHED THEN UPDATE SET v = n.v WHEN NOT MATCHED THEN INSERT VALUES (n.k, n.v)""")
    show(con, "WITH gone AS (DELETE FROM finance.reports.q3 WHERE v < 50 RETURNING *) SELECT * FROM gone",
         "DELETE inside a CTE")
    show(con, "SELECT * FROM finance.reports.q3")

    section("SQL: JSON mutation, UNNEST in GROUP BY")
    show(con, """SELECT json_set(j, '$.a', '2'::JSON) s, json_insert(j, '$.b', '3'::JSON) i,
                        json_remove(j, '$.a') r FROM (SELECT '{"a":1}'::JSON j)""")
    show(con, "SELECT unnest([1,2,2,3]) AS g, count(*) FROM range(1) GROUP BY unnest([1,2,2,3])")

    section("SQL: NEAREST join (top-k similarity)")
    show(con, """CREATE TABLE docs AS SELECT i AS id, [i::DOUBLE, (10 - i)::DOUBLE] AS emb FROM range(10) r(i);
                 CREATE TABLE queries AS SELECT * FROM (VALUES (1, [9.0, 1.0]), (2, [0.0, 9.0])) q(qid, emb)""")
    show(con, """SELECT q.qid, d.id FROM queries q
                 INNER JOIN docs d NEAREST 2 BY DISTANCE array_distance(q.emb::DOUBLE[2], d.emb::DOUBLE[2])
                 ORDER BY 1, 2""", "2 closest docs per query")
