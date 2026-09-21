import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import state_diff


class JsonHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            payload = {"ok": True, "version": 1}
            raw = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        self.send_error(404)

    def log_message(self, format, *args):
        pass


class StateDiffTests(unittest.TestCase):
    def test_canonical_hash_is_key_order_independent(self):
        a = {"z": 1, "a": {"b": 2}}
        b = {"a": {"b": 2}, "z": 1}
        self.assertEqual(state_diff.sha256_json(a), state_diff.sha256_json(b))

    def test_diff_reports_added_removed_type_and_value_changes(self):
        before = {"a": 1, "removed": True, "nested": {"type": 1, "value": "old"}}
        after = {"a": 1, "added": True, "nested": {"type": "1", "value": "new"}}
        changes = state_diff.diff_json(before, after)
        self.assertIn({"path": "removed", "change": "removed"}, changes)
        self.assertIn({"path": "added", "change": "added"}, changes)
        self.assertIn({
            "path": "nested.type",
            "change": "type_changed",
            "before_type": "integer",
            "after_type": "string",
        }, changes)
        self.assertIn({
            "path": "nested.value",
            "change": "value_changed",
            "before": "old",
            "after": "new",
        }, changes)

    def test_snapshot_diff_detects_endpoint_add_remove(self):
        before = {"endpoints": [{"path": "/a", "status": 200, "data": {"x": 1}},
                                {"path": "/gone", "status": 200, "data": {}}]}
        after = {"endpoints": [{"path": "/a", "status": 200, "data": {"x": 1}},
                               {"path": "/new", "status": 200, "data": {}}]}
        report = state_diff.diff_snapshots(before, after)
        self.assertTrue(report["changed"])
        self.assertEqual(report["endpoints_added"], ["/new"])
        self.assertEqual(report["endpoints_removed"], ["/gone"])

    def test_capture_endpoint_uses_get_and_parses_json(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            snap = state_diff.capture_endpoint(base, "/health", timeout=2)
            self.assertEqual(snap.status, 200)
            self.assertEqual(snap.data, {"ok": True, "version": 1})
            self.assertEqual(snap.path, "/health")
        finally:
            server.shutdown()
            server.server_close()

    def test_fail_on_change_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            before = td / "before.json"
            after = td / "after.json"
            before.write_text(json.dumps({"endpoints": [{"path": "/x", "status": 200, "data": {"a": 1}}]}))
            after.write_text(json.dumps({"endpoints": [{"path": "/x", "status": 200, "data": {"a": "1"}}]}))
            rc = state_diff.main(["diff", str(before), str(after), "--fail-on-change"])
            self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
