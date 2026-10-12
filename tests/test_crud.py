
import json
import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

import lambda_function


class TestCrawlerCRUD(unittest.TestCase):

    def test_create_invalid_url(self):
        """Unit test 1: Reject invalid URLs."""
        event = {
            "httpMethod": "POST",
            "body": json.dumps({"url": "invalid-url"})
        }

        result = lambda_function.lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 400)

    def test_unsupported_method(self):
        """Unit test 2: Reject unsupported HTTP methods."""
        event = {
            "httpMethod": "PATCH",
            "body": "{}"
        }

        result = lambda_function.lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 405)

    @patch.object(lambda_function, "table")
    def test_create_functional(self, mock_table):
        """Functional test: Verify POST behaviour."""
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "url": "https://example.com"
            })
        }

        result = lambda_function.lambda_handler(event, None)
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 201)
        self.assertEqual(
            body["item"]["url"],
            "https://example.com"
        )
        mock_table.put_item.assert_called_once()

    @patch.object(lambda_function, "table")
    def test_read_integration_mock(self, mock_table):
        """Mocked Lambda-DynamoDB interaction test."""
        mock_table.scan.return_value = {
            "Items": [
                {
                    "id": "test-1",
                    "url": "https://example.com",
                    "status": "pending"
                }
            ]
        }

        event = {"httpMethod": "GET"}
        result = lambda_function.lambda_handler(event, None)
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(len(body["items"]), 1)
        mock_table.scan.assert_called_once()


if __name__ == "__main__":
    unittest.main()
