"""JSON text column to typed columns: infer the shape, patch the types, unnest."""
from lib import section, show


def run(con):
    section("JSON TO TYPED COLUMNS")
    show(con, """CREATE TABLE raw AS SELECT * FROM (VALUES
        (1, '{"ts":"2026-10-21 09:00:00","user":{"id":7},"ms":120,"items":[{"sku":"a","qty":2}]}'),
        (2, '{"ts":"2026-10-21 09:05:00","user":{"id":8},"ms":95,"items":[{"sku":"b","qty":1},{"sku":"c","qty":4}]}')
      ) t(id, payload)""")
    show(con, "SELECT json_group_structure(payload::JSON) FROM raw", "infer one shape from every row")
    show(con, """SET VARIABLE shape = (SELECT json_merge_patch(json_group_structure(payload::JSON),
                 '{"ts":"TIMESTAMP","ms":"INTEGER","user":{"id":"INTEGER"},"items":[{"sku":"VARCHAR","qty":"INTEGER"}]}')
                 FROM raw)""", "patch only the types you want to change")
    show(con, """CREATE TABLE typed AS SELECT id, unnest(json_transform(payload, getvariable('shape'))) FROM raw""")
    show(con, "DESCRIBE typed")
    show(con, "SELECT id, u.item.sku, u.item.qty FROM typed, unnest(items) AS u(item) ORDER BY 1, 2",
         "arrays become rows")
    show(con, """SELECT json_transform('{"qty":"two"}', '{"qty":"INTEGER"}')""", "a bad value silently becomes NULL")
    show(con, """SELECT json_transform_strict('{"qty":"two"}', '{"qty":"INTEGER"}')""", "the strict version raises instead")
