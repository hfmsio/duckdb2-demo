"""Small additions from the 2.0 release notes."""
from lib import section, show


def run(con):
    section("SMALL ADDITIONS")
    show(con, "SELECT decimal_average(x) FROM (VALUES (1.10::DECIMAL(9,2)), (2.25)) t(x)", "average that stays DECIMAL")
    show(con, "SELECT variant_array_length('[1,2,3]'::JSON::VARIANT)")
    show(con, "SELECT a, b, sum(b) FROM (VALUES (1, 2), (1, 3), (2, 4)) t(a, b) GROUP BY ROLLUP (a, b) ORDER BY ALL",
         "ROLLUP/CUBE now plan as CTEs")
