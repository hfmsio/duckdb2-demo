# Support desk on DuckDB 2.0

One small story that uses DuckDB 2.0 "Cinnamon Teal" (released 2026-10-21) the way a real team might. Support tickets arrive as messy JSON and end up typed, audited, shared over the network, searchable by similarity, graphed, scored by a model and time-travelled. Everything runs live against `duckdb==2.0.0`. Tested on macOS arm64 with Python 3.12. Unofficial, not affiliated with DuckDB Labs.

![demo](docs/demo.gif)

```
make demo               # the whole story
make demo ARGS="4 5"    # chosen acts
```

## Run it

Needs Python 3.11 or newer (the `duckdb` 2.0 wheels require it) and `make`. `make demo` creates a `.venv`, installs `requirements.txt` and runs the story. If `python3` is older, use `make PYTHON=python3.12`. The first run downloads the `duckpgq`, `typed_ai`, `ducklake` and `quack` extensions, so it needs internet.

Act 8 needs the 2.0 CLI, because a CLI from 1.x has no agent mode. Download it from the [v2.0.0 release](https://github.com/duckdb/duckdb/releases/tag/v2.0.0) and set `DUCKDB_CLI=/path/to/duckdb`. Without it the act is skipped.

## The acts

| Act | What it does | Features |
|---|---|---|
| 1. Ingest JSON | Infers a schema from raw JSON text, patches the types, and builds a typed `tickets` table. The raw text is kept in a `VARIANT` column and queried with dot paths. | `json_group_structure`, `json_transform`, `VARIANT` |
| 2. Triggers | An `AFTER INSERT` row trigger writes one audit row per ticket. A statement trigger on the `inbox` table counts the rows in each batch. New tickets move from `inbox` to `tickets` in one `INSERT ... SELECT`. | `CREATE TRIGGER`, `REFERENCING NEW TABLE` |
| 3. Quack server | Serves the database with `quack_serve`. Three clients append a batch each at the same time. A dashboard client runs `CONNECT` and its queries execute on the server. | Quack, `ATTACH`, `CONNECT` |
| 4. Similarity search | Finds the closest solved ticket for each open ticket with `array_distance` over a toy keyword embedding. The embedding macro uses the new lambda syntax. | `NEAREST` join, `lambda` |
| 5. Graph queries | Models customers and tickets as a property graph, then matches customer, opened ticket, duplicate of the root outage ticket. | DuckPGQ, extensible parser |
| 6. Model scoring with a spend cap | Asks a model a yes/no question for every ticket. A dry run prices the query without calling the model, and `typed_budget_usd` caps spend. | `typed_ai` community extension |
| 7. Snapshots | Writes a daily summary into a DuckLake table, one snapshot per load, then reads the table as it was after the first load. | DuckLake, `AT (VERSION => n)` |
| 8. CLI agent mode | Runs a valid query and a query with a typo through the 2.0 CLI. Output is a compact markdown table and a JSON error. | `duckdb -agent` |

The AI act is a dry run by default: it prices the query and calls no model. `DEMO_LIVE=1` makes real calls with `TYPESAFE_API_KEY` and costs cents.

## Notes from building it

- `x -> x + 1` lambdas are an error. Write `lambda x: x + 1`.
- Python relations have no `fetchone()`. Use `con.execute(sql).fetchone()`.
- A file written by 2.0 cannot be opened by 1.5.5. Upgrade on copies.
- Quack: parallel inserts from 8 clients all landed. Updates to one row from 8 clients conflicted (48 of 200 in one run) and need a retry loop. The token must be at least 4 characters.
- Triggers: no `UPDATE ... FOR EACH ROW`. Row and statement triggers cannot share a table. `MERGE INTO` is refused on a table that has triggers.
- `CONNECT` to PostgreSQL ran aggregates on the server, but `EXPLAIN` through it fails.
- DuckPGQ parses only after `SET active_grammar_extensions = ['duckpgq']`, and a pattern edge needs a name: `-[e:knows]->`.
- On 2026-10-22 the `ai`, `duckdb_mcp`, `faiss`, `quackformers` and `jev` extensions had no 2.0.0 download for macOS arm64. `typed_ai` did.
- Agent mode, per DuckDB's own benchmark: 59% fewer output tokens read, about 0.5% of total input, so cost and runtime did not change. [Source](https://duckdb.org/2026/10/09/agent-mode).

`tour/` holds a one-feature-at-a-time version of the same checks (`make tour`). `make tour ARGS=remote` runs `CONNECT` against a throwaway PostgreSQL container, so it needs Docker.

For anything beyond a demo, put a TLS-terminating reverse proxy in front of Quack, as the release notes advise. Numbers come from one laptop. Release: [Announcing DuckDB 2.0.0 LTS](https://duckdb.org/2026/10/21/announcing-duckdb-200).

MIT licensed. See [LICENSE](LICENSE).
