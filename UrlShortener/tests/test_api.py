import unittest

from fastapi.testclient import TestClient

from UrlShortener.api import app

client = TestClient(app)


class TestApi(unittest.TestCase):

    def test_shorten_url(self):
        long_url = "https://example.com/"
        response = client.post("/shorten", json={"url": long_url})
        self.assertEqual(response.status_code, 200)
        self.assertIn("shortened_url", response.json())

    def test_redirect_url(self):
        long_url = "https://example.com/"
        response = client.post("/shorten", json={"url": long_url})
        short_url = response.json()["shortened_url"]
        response = client.get(short_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("url", response.json())
        self.assertEqual(response.json()["url"], long_url)

    def test_invalid_short_code(self):
        invalid_short_code = "invalid"
        response = client.get(invalid_short_code)
        self.assertEqual(response.status_code, 404)
