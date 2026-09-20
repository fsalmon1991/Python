import unittest

import smoke


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = {
            "/health": {
                "ok": True,
                "version": "2.2.1-rip200",
                "uptime_s": 64177,
            },
            "/epoch": {
                "blocks_per_epoch": 144,
                "enrolled_miners": 17,
                "epoch": 290,
                "slot": 41902,
            },
            "/api/miners": {
                "miners": [
                    {
                        "miner": "example-wallet",
                        "device_arch": "modern",
                        "device_family": "x86",
                        "last_attest": 1789848266,
                    }
                ],
                "pagination": {"count": 1, "total": 1, "total_enrolled": 17},
            },
        }

    def fetcher(self, url, timeout, insecure):
        for path, payload in self.fixtures.items():
            if url.endswith(path):
                return 200, payload, 12.345
        raise AssertionError(url)

    def test_all_contracts_pass_with_current_shapes(self):
        results = smoke.run_checks("https://rustchain.org", fetcher=self.fetcher)
        self.assertEqual(3, len(results))
        self.assertTrue(all(r.ok for r in results))
        self.assertEqual(17, results[1].summary["enrolled_miners"])
        self.assertEqual(1, results[2].summary["returned_miners"])

    def test_missing_required_key_fails(self):
        def broken(url, timeout, insecure):
            return 200, {"ok": True}, 1.0

        result = smoke.check_endpoint(
            "https://rustchain.org",
            smoke.SPECS[0],
            timeout=1.0,
            insecure=False,
            fetcher=broken,
        )
        self.assertFalse(result.ok)
        self.assertIn("version", result.errors[0])

    def test_http_error_fails(self):
        def broken(url, timeout, insecure):
            return 503, {"ok": False, "version": "2.2.1-rip200"}, 5.0

        result = smoke.check_endpoint(
            "https://rustchain.org",
            smoke.SPECS[0],
            timeout=1.0,
            insecure=False,
            fetcher=broken,
        )
        self.assertFalse(result.ok)
        self.assertIn("HTTP 503", result.errors)

    def test_miner_nested_schema_is_checked(self):
        def broken(url, timeout, insecure):
            return 200, {"miners": [{"miner": "x"}], "pagination": {}}, 1.0

        result = smoke.check_endpoint(
            "https://rustchain.org",
            smoke.SPECS[2],
            timeout=1.0,
            insecure=False,
            fetcher=broken,
        )
        self.assertFalse(result.ok)
        self.assertTrue(any("device_arch" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
