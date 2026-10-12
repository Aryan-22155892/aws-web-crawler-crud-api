
import os
import json
import time
import unittest
import urllib.request
import urllib.error


BASE_URL = os.environ.get("API_BASE_URL", "").rstrip("/")


@unittest.skipUnless(
    BASE_URL,
    "API_BASE_URL not configured"
)
class TestLiveIntegration(unittest.TestCase):

    def request_api(self, method, path, data=None):
        body = json.dumps(data).encode() if data else None
        request = urllib.request.Request(
            BASE_URL + path,
            data=body,
            headers={"Content-Type": "application/json"},
            method=method
        )

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(
                request, timeout=15
            ) as response:
                status = response.status
                result = json.loads(response.read())
        except urllib.error.HTTPError as error:
            status = error.code
            result = json.loads(error.read())

        elapsed = round(
            (time.perf_counter() - start) * 1000, 2
        )
        print(f"{method} {path}: {elapsed} ms")
        print(
            "Reported operation time:",
            result.get("dynamodb_operation_ms"),
            "ms"
        )
        return status, result

    def test_complete_crud_workflow(self):
        target_id = None

        try:
            status, created = self.request_api(
                "POST",
                "/targets",
                {"url": "https://example.com"}
            )
            self.assertEqual(status, 201)
            target_id = created["item"]["id"]

            status, fetched = self.request_api(
                "GET", f"/targets/{target_id}"
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                fetched["url"], "https://example.com"
            )

            status, updated = self.request_api(
                "PUT",
                f"/targets/{target_id}",
                {"url": "https://www.wikipedia.org"}
            )
            self.assertEqual(status, 200)

            status, fetched = self.request_api(
                "GET", f"/targets/{target_id}"
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                fetched["url"],
                "https://www.wikipedia.org"
            )

            status, deleted = self.request_api(
                "DELETE", f"/targets/{target_id}"
            )
            self.assertEqual(status, 200)
            target_id = None

        finally:
            if target_id:
                self.request_api(
                    "DELETE", f"/targets/{target_id}"
                )


if __name__ == "__main__":
    unittest.main()
