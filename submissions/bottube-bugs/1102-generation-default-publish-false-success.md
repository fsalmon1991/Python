# BoTTube functional bug report — generation can report “published” after DB insert failure

**Bounty:** Scottcjn/rustchain-bounties#1102  
**Target:** Scottcjn/bottube  
**Claimant:** @fsalmon1991  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**Source commit reviewed:** `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1` (2026-09-19)

## Summary

The default video-generation publisher swallows every database-insert exception, but both callers treat `_default_publish()` as if publication succeeded. A generation job can therefore be marked `completed` and expose a `videoUrl` / `watchUrl` even though no row was inserted into `videos`.

This is a functional false-success bug, not a cosmetic issue. It affects both the automatic generation pipeline and the authenticated manual `/api/generation/jobs/<job_id>/publish` path when the injected publisher is absent.

## Affected code

### 1. `_default_publish()` logs DB failure and returns normally

`generation/worker.py` opens the BoTTube SQLite DB, converts `owner_user_id` to `int`, inserts into `videos`, commits, and closes the connection. The entire operation is wrapped in:

```python
try:
    conn = sqlite3.connect(str(_DB_PATH))
    ...
    conn.execute("""INSERT INTO videos ...""", (...))
    conn.commit()
    conn.close()
    log.info("Video %s inserted into DB ...", video_id)
except Exception as exc:
    log.error("Failed to insert video record: %s", exc)
```

There is no re-raise and no success/failure return value.

Current source:  
https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/generation/worker.py

### 2. Automatic pipeline marks the job completed unconditionally

Immediately after calling `_default_publish(...)`, `_run_pipeline()` does:

```python
_default_publish(job_id, video_id, final_path, req, provider_name)
update_job(
    job_id,
    status=JobStatus.completed.value,
    video_url=f"https://bottube.ai/api/videos/{video_id}/stream",
    progress=100,
    completed_at=time.time(),
)
log.info("Job %s published as video %s (default publisher)", job_id, video_id)
return
```

So a failed insert becomes a successful completed job.

### 3. Manual publish endpoint has the same false-success path

`generation/routes.py` calls `_default_publish(...)` and then unconditionally sets:

```python
update_job(
    job_id,
    video_id=video_id,
    video_url=f"https://bottube.ai/api/videos/{video_id}/stream",
    requires_approval=False,
    status=JobStatus.completed.value,
)

return jsonify({
    "ok": True,
    "status": "published",
    "watchUrl": f"https://bottube.ai/watch/{video_id}",
})
```

Current source:  
https://github.com/Scottcjn/bottube/blob/0b25f2bed262746a653c86ef2a1b8b0f5b2794a1/generation/routes.py

## Reproduction

This can be reproduced locally without touching production data.

1. Create or select a generation job that has reached the publish stage and uses the default publisher (`publish_fn is None`).
2. Force any failure inside `_default_publish()` after entry. Safe examples in a local test DB:
   - point `_DB_PATH` to a SQLite DB without a `videos` table;
   - use a fixture whose `videos` table is missing one of the source columns;
   - monkeypatch `sqlite3.connect` / `conn.execute` so the INSERT raises `sqlite3.OperationalError("forced insert failure")`;
   - supply a local fixture where `owner_user_id` cannot be converted to `int`.
3. Call the automatic publish branch or POST the manual `/api/generation/jobs/<job_id>/publish` route for that local fixture.
4. `_default_publish()` catches the exception and returns normally.
5. Observe the job is marked `completed`; the manual endpoint also returns `ok: true`, `status: published`, and a `watchUrl`.
6. Query `videos` for the generated `video_id`. No row exists.

### Minimal regression-test shape

```python
def test_default_publish_failure_does_not_mark_job_completed(monkeypatch, ...):
    class BrokenConn:
        row_factory = None
        def execute(self, *args, **kwargs):
            raise sqlite3.OperationalError("forced insert failure")

    monkeypatch.setattr(worker.sqlite3, "connect", lambda *a, **k: BrokenConn())

    # Arrange a job already ready to publish, then invoke the default-publish path.
    # Expected after the fix: failed status / 500, no published URL.
    # Current behavior: completed / ok:true with a URL despite no DB row.
```

A route-level test should make the same injected failure and assert the manual publish endpoint returns a failure response instead of `200 {"ok": true, ...}`.

## Expected

Publication success must mean the `videos` row was durably inserted. If DB publication fails, the caller should receive/record failure and must not emit a usable-looking video/watch URL.

## Actual

`_default_publish()` converts publication failure into a log-only event. Its callers cannot distinguish success from failure and mark the job published anyway.

## Impact

- API clients can receive a successful publish response for a video that does not exist in the DB.
- Job polling can show `completed` / `progress=100` when publication failed.
- Consumers can be handed dead `/stream` and `/watch/<id>` URLs.
- Automated agents may treat the false positive as a durable publication and move on, losing the generated artifact after work-dir cleanup.
- Operational DB/schema/lock failures become harder to detect because the API-level state contradicts persistence.

## Suggested fix

Make persistence failure observable to the caller. Two clean options:

1. Let `_default_publish()` raise on failure and have callers translate that into job `failed` / HTTP 500; or
2. Return an explicit success/failure result and require callers to branch on it before setting `completed`.

Also use a context manager or `finally` block so the SQLite connection is closed on all exception paths.

Recommended regression coverage:

- automatic pipeline + forced DB insert failure → job is not `completed`, no published URL;
- manual publish + forced DB insert failure → HTTP 500 (or equivalent), `requires_approval` remains true, no fake watch URL;
- successful DB insert → existing completion behavior remains unchanged.

## Duplicate check

Before filing, I searched the current BoTTube issue set and RustChain bounty tracker for the exact implementation names / failure text:

- `_default_publish`
- `Failed to insert video record`
- `default publisher` + `generation`

I did not find an existing report for this false-success behavior.

## Environment / validation note

This report is based on direct source inspection of current BoTTube main at commit `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`. I did not send destructive or malformed requests to production. The failure path is deterministic from the control flow above and is suitable for a local fixture/monkeypatch regression test.

## AI disclosure

This report was researched and drafted with AI assistance under @fsalmon1991. The cited code paths and current commit were checked directly before submission.
