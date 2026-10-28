import os
import duckdb
from common.ui import act, say, show


def run(ctx):
    act(6, "Model scoring with a spend cap", "typed_ai asks a yes/no question per row. A dry run prices the query without calling a model.")
    live = os.environ.get("DEMO_LIVE") == "1"
    con = duckdb.connect(ctx["db"], read_only=True)
    show(con, "INSTALL typed_ai FROM community; LOAD typed_ai")
    show(con, "SET typed_budget_usd = 0.01")
    if live:
        show(con, "CREATE SECRET jev (TYPE typed_ai, PROVIDER 'jev', API_KEY getenv('TYPESAFE_API_KEY'))")
    else:
        say("Dry run: prices the query and calls no model. Set DEMO_LIVE=1 for real answers.")
        show(con, "SET typed_dry_run = true")
    show(con, "SELECT id, subject, typed_prob(tickets, 'the customer is about to cancel') AS risk FROM tickets", rows=3)
    show(con, "SELECT round(spent_usd, 6) AS spent_usd, round(dry_run_usd, 6) AS would_cost_usd FROM typed_usage()")
    con.close()
