# BoTTube bug report: translated-language API duplicates videos across translators

**Target:** `Scottcjn/bottube`

**Validated source revision:** `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`

**Bounty routing:** `Scottcjn/rustchain-bounties#71` (ongoing bug bounty)

**Requested tier:** Low — 5 RTC, subject to maintainer validation

**RTC payout wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

`GET /api/videos/translated/<language>` returns one row per **translation record**, rather than one row per video. The schema permits multiple translators to submit the same language for the same video because the uniqueness constraint is `(video_id, language, translator_id)`. The language-feed query then joins every matching translation row, so one video is returned multiple times when two translators have translated it into the same language.

This is a functional data-shape bug: clients can render duplicate videos, counts are inflated, and any downstream pagination/ranking based on the returned rows can be wrong.

## Affected code

The current schema in `translation_routes.py` contains:

```sql
UNIQUE(video_id, language, translator_id)
```

The current `/api/videos/translated/<language>` query is:

```sql
SELECT v.*, vt.title as translated_title, vt.description as translated_description
FROM videos v
JOIN video_translations vt ON v.video_id = vt.video_id
JOIN agents a ON a.id = v.agent_id
WHERE vt.language = ?
  AND COALESCE(v.is_removed, 0) = 0
  AND COALESCE(a.is_banned, 0) = 0
ORDER BY vt.created_at DESC
```

Those two contracts conflict if the endpoint is intended to list translated **videos**: the table is many-translations-per-video/language, while the query returns every translation as a separate video row.

## Minimal reproduction

The following uses the current uniqueness rule and exact query shape:

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
con.executescript("""
CREATE TABLE agents(
    id INTEGER PRIMARY KEY,
    is_banned INTEGER DEFAULT 0
);
CREATE TABLE videos(
    video_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    agent_id INTEGER,
    is_removed INTEGER DEFAULT 0
);
CREATE TABLE video_translations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    language TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    translator_id INTEGER NOT NULL,
    created_at REAL NOT NULL DEFAULT (unixepoch()),
    UNIQUE(video_id, language, translator_id)
);
""")

con.executemany("INSERT INTO agents(id) VALUES (?)", [(1,), (2,), (3,)])
con.execute(
    "INSERT INTO videos(video_id,title,description,agent_id) VALUES (?,?,?,?)",
    ("v1", "Original", "D", 1),
)
con.execute(
    """INSERT INTO video_translations
       (video_id,language,title,description,translator_id,created_at)
       VALUES (?,?,?,?,?,?)""",
    ("v1", "Spanish", "Uno", "A", 2, 100),
)
con.execute(
    """INSERT INTO video_translations
       (video_id,language,title,description,translator_id,created_at)
       VALUES (?,?,?,?,?,?)""",
    ("v1", "Spanish", "Dos", "B", 3, 200),
)

rows = con.execute("""
SELECT v.*, vt.title as translated_title, vt.description as translated_description
FROM videos v
JOIN video_translations vt ON v.video_id = vt.video_id
JOIN agents a ON a.id = v.agent_id
WHERE vt.language = ?
  AND COALESCE(v.is_removed, 0) = 0
  AND COALESCE(a.is_banned, 0) = 0
ORDER BY vt.created_at DESC
""", ("Spanish",)).fetchall()

print([dict(row) for row in rows])
```

Observed output contains `video_id='v1'` twice:

```text
[
  {'video_id': 'v1', ..., 'translated_title': 'Dos', 'translated_description': 'B'},
  {'video_id': 'v1', ..., 'translated_title': 'Uno', 'translated_description': 'A'}
]
```

## Expected

A translated-language video listing should return each `video_id` once, with a deterministic translation-selection rule. The simplest rule is newest translation for `(video_id, language)`, although an explicit approved/preferred translation would be even clearer if that concept exists elsewhere.

## Actual

Every translator row becomes another copy of the same video in the response.

## Suggested fix

Select one translation per `(video_id, language)` before joining to `videos`. For example, rank rows using:

```sql
ROW_NUMBER() OVER (
  PARTITION BY video_id, language
  ORDER BY created_at DESC, id DESC
)
```

and keep only rank 1. A correlated subquery selecting the newest translation `id` is another compatible option.

Add a regression test where two distinct translators create Spanish translations for the same video and assert that `/api/videos/translated/Spanish` returns exactly one row for that `video_id`.

## Duplicate check

I searched existing `Scottcjn/bottube` issues for translation duplicates, translated-language duplicates, translator/language collisions, and `/api/videos/translated`. The directly related issue I found was `#2234`, which is about mixed timestamp types and recency ordering, not duplicate video rows.

## Safety / validation notes

This was reproduced entirely against an in-memory SQLite database using the current source query. No production writes, destructive actions, authentication bypass attempts, or load testing were performed.

AI assistance was used for source inspection, duplicate checking, reproduction, and report preparation.
