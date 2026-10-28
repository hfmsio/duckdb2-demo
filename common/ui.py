"""Story output helpers: headings, narration, and statements printed with their results."""
import re


def _heading(kind):
    def head(n, title, blurb):
        print(f"\n\n  {kind} {n}: {title}\n  {blurb}")
    return head


act, recipe = _heading("ACT"), _heading("RECIPE")


def say(text):
    print(f"\n  # {text}")


def show(con, sql, rows=6):
    print("\n  > " + re.sub(r"\s+", " ", sql).strip()[:200])
    try:
        out = con.execute(sql).fetchall()
    except Exception as e:
        print(f"    ERR {str(e).splitlines()[0][:140]}")
        return None
    for r in out[:rows]:
        print("   ", r)
    if len(out) > rows:
        print(f"    ... {len(out)} rows")
    return out
