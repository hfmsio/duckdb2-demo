"""typed_ai community extension (DuckDB 2.0 build): ask a model typed questions about rows.
Default is a dry run: prices the query, calls nothing. DEMO_LIVE=1 spends real money (cents) using TYPESAFE_API_KEY."""
import os
import duckdb
from lib import section, show


def run():
    section("AI: typed_ai community extension")
    live = os.environ.get("DEMO_LIVE") == "1"
    con = duckdb.connect()
    show(con, "INSTALL typed_ai FROM community; LOAD typed_ai", "built for 2.0 on day one")
    show(con, "SELECT function_name FROM duckdb_functions() WHERE function_name LIKE 'typed_%' GROUP BY 1 ORDER BY 1")
    show(con, "SET typed_budget_usd = 0.01", "hard spend cap, enforced from the first query")
    if live:
        show(con, "CREATE SECRET jev (TYPE typed_ai, PROVIDER 'jev', API_KEY getenv('TYPESAFE_API_KEY'))")
    else:
        show(con, "SET typed_dry_run = true", "price the query, call nothing, results are NULL")
    show(con, """CREATE TABLE found AS FROM (VALUES ('insulin pen', 'waiting room'), ('half-eaten sandwich', 'train to Leeds'))
                 t(item, place)""")
    show(con, "SELECT item, typed_prob(item, 'the owner needs this back today') AS urgent FROM found",
         "probability from the model's own odds" if live else "NULL in dry run")
    show(con, "SELECT item FROM found f WHERE typed_is(f, 'it was left on a train')", "a yes/no filter inside WHERE")
    show(con, "SELECT provider, spent_usd, dry_run_usd, requests FROM typed_usage()",
         "what it would cost vs what it spent")
