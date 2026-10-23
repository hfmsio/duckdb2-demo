"""Deterministic fake support tickets, as the JSON text a webhook would send."""
import json
import random

CUSTOMERS = [(i, n, p) for i, (n, p) in enumerate(
    [("Acme", "pro"), ("Birch", "free"), ("Cobalt", "pro"), ("Delta", "team"), ("Ember", "free"),
     ("Fjord", "team"), ("Glow", "pro"), ("Harbor", "free")], 1)]
TOPICS = {
    "refund": ("billing", "I was charged twice and want a refund", "Duplicate charge on my invoice, please refund it"),
    "login": ("app", "I cannot log in after the update", "Login loop after password reset, the app keeps signing me out"),
    "outage": ("api", "The API is down again", "Requests time out with 503 errors since this morning"),
    "wifi": ("router", "Router drops wifi every hour", "Wifi disconnects hourly, restarting the router helps briefly"),
}


def tickets(n, start=1, seed=7):
    rnd = random.Random(seed + start)
    out = []
    for i in range(start, start + n):
        topic = rnd.choice(list(TOPICS))
        product, subject, body = TOPICS[topic]
        cid, name, plan = rnd.choice(CUSTOMERS)
        out.append((i, json.dumps({
            "ts": f"2026-10-{rnd.randint(18, 21)} {rnd.randint(8, 17):02d}:{rnd.randint(0, 59):02d}:00",
            "customer": {"id": cid, "name": name, "plan": plan}, "product": product, "channel": rnd.choice(["email", "chat"]),
            "subject": subject, "body": body, "tags": [topic], "resolved": rnd.random() < 0.6,
            "resolution": {"refund": "Refunded the duplicate charge", "login": "Cleared sessions and reset the token",
                           "outage": "Restarted the gateway, root cause was a bad deploy",
                           "wifi": "Updated router firmware to 4.2"}[topic]})))
    return out


def insert_sql(table, rows):
    """One multi-row INSERT, so a statement-level trigger sees the whole batch."""
    return f"INSERT INTO {table} VALUES " + ", ".join(f"({i}, '{p.replace(chr(39), chr(39) * 2)}')" for i, p in rows)
