"""CREATE TRIGGER: row-level audit trail and a statement-level rollup.
2.0 limits: no UPDATE row triggers yet, and row and statement triggers cannot share a table."""
from lib import section, show


def run(con):
    section("TRIGGERS")
    show(con, """CREATE TABLE orders(id INT, qty INT); CREATE TABLE audit(id INT, what VARCHAR);
                 CREATE TABLE stock(sku INT); CREATE TABLE batches(n BIGINT)""")
    show(con, "CREATE TRIGGER t_ins AFTER INSERT ON orders FOR EACH ROW INSERT INTO audit VALUES (NEW.id, 'insert')")
    show(con, "CREATE TRIGGER t_del AFTER DELETE ON orders FOR EACH ROW INSERT INTO audit VALUES (OLD.id, 'delete')")
    show(con, """CREATE TRIGGER t_batch AFTER INSERT ON stock REFERENCING NEW TABLE AS added FOR EACH STATEMENT
                 INSERT INTO batches SELECT count(*) FROM added""")
    show(con, "INSERT INTO orders VALUES (1, 5), (2, 7); DELETE FROM orders WHERE id = 1")
    show(con, "SELECT * FROM audit ORDER BY what, id", "row-level audit trail")
    show(con, "INSERT INTO stock VALUES (1), (2), (3)")
    show(con, "SELECT * FROM batches", "one row for the whole 3-row insert")
    show(con, "SELECT trigger_name, table_name FROM duckdb_triggers() ORDER BY 1", "triggers are catalog objects")
    show(con, "DROP TRIGGER t_del ON orders")
