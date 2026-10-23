"""Tiny helpers: run a statement, print it with its result, never crash the tour."""
import re


def section(title):
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def show(con, sql, note=""):
    flat = re.sub(r"\s+", " ", sql).strip()
    print(f"\n> {flat}" + (f"   -- {note}" if note else ""))
    try:
        rows = con.execute(sql).fetchall()
    except Exception as e:
        print(f"  ERR {str(e).splitlines()[0][:150]}")
        return None
    for r in rows[:6]:
        print("  ", r)
    if len(rows) > 6:
        print(f"   ... {len(rows)} rows")
    return rows
