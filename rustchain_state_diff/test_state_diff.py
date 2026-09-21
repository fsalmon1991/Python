import unittest

import state_diff


class StateDiffTests(unittest.TestCase):
    def setUp(self):
        self.payloads = {
            "/health": {"ok": True, "version": "2.2.1-rip200"},
            "/epoch": {
                "epoch": 290,
                "slot": 41902,
                "blocks_per_epoch": 144,
                "enrolled_miners": 17,
            },
            "/api/miners": {
                "miners": [
                    {
                        "miner": "alpha",
                        "device_arch": "modern",
                        "device_family": "x86",
                        "last_attest": 100,
                        "fingerprint_passed": True,
                    }
                ],
                "pagination": {"total": 1, "total_enrolled": 17},
            },
        }

    def fetcher(self, url, timeout, insecure):
        for path, payload in self.payloads.items():
            if url.endswith(path):
                return payload
        raise AssertionError(url)

    def test_capture_normalizes_current_public_shapes(self):
        snap = state_diff.make_snapshot(
            "https://rustchain.org/",
            fetcher=self.fetcher,
            captured_at=123,
        )
        self.assertEqual("https://rustchain.org", snap["node"])
        self.assertEqual(290, snap["epoch"]["epoch"])
        self.assertEqual(17, snap["miner_summary"]["total_enrolled"])
        self.assertTrue(snap["miner_summary"]["miners"]["alpha"]["fingerprint_passed"])

    def test_added_removed_and_changed_miners_are_reported(self):
        old = {
            "captured_at": 1,
            "node": "n",
            "health": {"ok": True, "version": "v"},
            "epoch": {"epoch": 1},
            "miner_summary": {
                "miners": {
                    "alpha": {"last_attest": 1},
                    "gone": {"last_attest": 1},
                }
            },
        }
        new = {
            "captured_at": 2,
            "node": "n",
            "health": {"ok": True, "version": "v"},
            "epoch": {"epoch": 1},
            "miner_summary": {
                "miners": {
                    "alpha": {"last_attest": 2},
                    "beta": {"last_attest": 2},
                }
            },
        }
        diff = state_diff.diff_snapshots(old, new)
        self.assertEqual(["beta"], diff["miner_changes"]["added"])
        self.assertEqual(["gone"], diff["miner_changes"]["removed"])
        self.assertIn("alpha", diff["miner_changes"]["changed"])
        self.assertTrue(diff["changed"])

    def test_health_true_to_false_is_a_regression(self):
        old = {
            "health": {"ok": True, "version": "v1"},
            "epoch": {},
            "miner_summary": {"miners": {}},
        }
        new = {
            "health": {"ok": False, "version": "v1"},
            "epoch": {},
            "miner_summary": {"miners": {}},
        }
        diff = state_diff.diff_snapshots(old, new)
        self.assertEqual(1, len(diff["regressions"]))
        self.assertEqual("health.ok", diff["regressions"][0]["path"])

    def test_version_change_is_visible_but_not_a_health_regression(self):
        old = {
            "health": {"ok": True, "version": "v1"},
            "epoch": {},
            "miner_summary": {"miners": {}},
        }
        new = {
            "health": {"ok": True, "version": "v2"},
            "epoch": {},
            "miner_summary": {"miners": {}},
        }
        diff = state_diff.diff_snapshots(old, new)
        self.assertTrue(diff["changed"])
        self.assertEqual([], diff["regressions"])

    def test_invalid_miner_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            state_diff.summarize_miners({"miners": {}})


if __name__ == "__main__":
    unittest.main()
