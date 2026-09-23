import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_economy_grazer import AgentEconomyError, AgentEconomyGrazer


class Handler(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        parsed = urlparse(self.path)
        Handler.requests.append((parsed.path, parse_qs(parsed.query)))
        if parsed.path == "/agent/jobs":
            payload = {
                "ok": True,
                "jobs": [
                    {
                        "job_id": "job_alpha",
                        "title": "Research RustChain hardware",
                        "description": "Compare vintage silicon reward behavior",
                        "category": "research",
                        "status": "open",
                        "reward_rtc": 12.5,
                        "poster_wallet": "poster1",
                        "worker_wallet": None,
                        "created_at": 10,
                        "tags": '["hardware", "antiquity"]',
                    },
                    {
                        "job_id": "job_beta",
                        "title": "Write protocol notes",
                        "description": "Document marketplace API behavior",
                        "category": "writing",
                        "status": "open",
                        "reward_rtc": "4.0",
                        "poster_wallet": "poster2",
                        "worker_wallet": "worker1",
                        "created_at": "11",
                        "tags": ["docs"],
                    },
                ],
                "total": 2,
                "limit": 50,
                "offset": 0,
                "categories": ["research", "writing"],
            }
            return self._json(200, payload)
        if parsed.path == "/agent/jobs/job_alpha":
            return self._json(200, {"ok": True, "job": {"job_id": "job_alpha"}, "activity": []})
        if parsed.path == "/agent/reputation/RTC_demo":
            return self._json(200, {"ok": True, "wallet": "RTC_demo", "trust_score": 88})
        if parsed.path == "/agent/stats":
            return self._json(200, {"ok": True, "total_jobs": 9, "active_agents": 3})
        if parsed.path == "/agent/jobs/job_missing":
            return self._json(404, {"error": "Job not found"})
        return self._json(404, {"error": "not found"})

    def _json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class AgentEconomyGrazerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        Handler.requests = []
        self.client = AgentEconomyGrazer(self.base_url, timeout=2)

    def test_browse_maps_supported_server_filters(self):
        page = self.client.browse(category="research", status="open", limit=25, offset=5, min_reward=2.5)
        self.assertEqual(page["total"], 2)
        self.assertEqual(len(page["results"]), 2)
        path, query = Handler.requests[-1]
        self.assertEqual(path, "/agent/jobs")
        self.assertEqual(query["category"], ["research"])
        self.assertEqual(query["status"], ["open"])
        self.assertEqual(query["limit"], ["25"])
        self.assertEqual(query["offset"], ["5"])
        self.assertEqual(query["min_reward"], ["2.5"])

    def test_search_is_local_read_only_keyword_discovery(self):
        results = self.client.search("antiquity")
        self.assertEqual([r["job_id"] for r in results], ["job_alpha"])
        self.assertEqual(len(Handler.requests), 1)
        self.assertEqual(Handler.requests[0][0], "/agent/jobs")

    def test_search_matches_description_and_category(self):
        self.assertEqual(self.client.search("marketplace")[0]["job_id"], "job_beta")
        self.assertEqual(self.client.search("research")[0]["job_id"], "job_alpha")

    def test_detail_reputation_and_stats(self):
        self.assertEqual(self.client.job("job_alpha")["job"]["job_id"], "job_alpha")
        self.assertEqual(self.client.reputation("RTC_demo")["trust_score"], 88)
        self.assertEqual(self.client.stats()["active_agents"], 3)

    def test_http_error_is_exposed_without_fabricating_result(self):
        with self.assertRaisesRegex(AgentEconomyError, "HTTP 404: Job not found"):
            self.client.job("job_missing")

    def test_validation_blocks_bad_filters(self):
        for kwargs in (
            {"limit": 0},
            {"limit": 101},
            {"offset": -1},
            {"min_reward": -0.01},
            {"category": "invalid"},
            {"status": "invalid"},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    self.client.browse(**kwargs)
        with self.assertRaises(ValueError):
            self.client.search(" ")

    def test_identifier_is_percent_encoded(self):
        with self.assertRaises(AgentEconomyError):
            self.client.job("../../agent/stats")
        self.assertIn("%2F", Handler.requests[-1][0] if Handler.requests else "")

    def test_read_only_surface_has_no_mutation_methods(self):
        for name in ("claim", "deliver", "accept", "dispute", "cancel", "post_job"):
            self.assertFalse(hasattr(self.client, name), name)


if __name__ == "__main__":
    unittest.main()
