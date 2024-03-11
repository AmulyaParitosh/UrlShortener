import unittest

from fastapi.testclient import TestClient

from UrlShortener.api import app

client = TestClient(app)


class TestURLShortener(unittest.TestCase):

    def test_shorten_url(self):
        long_url = "https://example.com"
        response = client.post("/shorten/", json={"long_url": long_url})
        self.assertEqual(response.status_code, 200)
        self.assertIn("shortened_url", response.json())

    def test_redirect_url(self):
        long_url = "https://example.com"
        response = client.post("/shorten/", json={"long_url": long_url})
        short_url = response.json()["shortened_url"]
        response = client.get(short_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("redirect_url", response.json())
        self.assertEqual(response.json()["redirect_url"], long_url)

    def test_invalid_short_code(self):
        invalid_short_code = "invalid"
        response = client.get(f"/{invalid_short_code}")
        self.assertEqual(response.status_code, 404)
