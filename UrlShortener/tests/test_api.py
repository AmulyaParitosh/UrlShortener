import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from UrlShortener.api import app

client = TestClient(app)


class TestApi(unittest.TestCase):

    @patch("UrlShortener.src.routes.api_routes.search_doc_by_long_url")
    @patch("UrlShortener.src.routes.api_routes.save_doc")
    @patch("UrlShortener.src.routes.api_routes.remove_expired_urls")
    @patch("UrlShortener.src.routes.api_routes.URLMapSchema")
    def test_shorten_url(
        self,
        mock_URLMapSchema,
        mock_remove_expired_urls,
        mock_save_doc,
        mock_search_doc_by_long_url,
    ):
        mock_search_doc_by_long_url.side_effect = KeyError
        mock_URLMapSchema.return_value = MagicMock(
            long_url="http://example.com", code="abcdef", model_dump=MagicMock()
        )
        response = client.post("/api/shorten", json={"url": "http://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"url": "http://testserver/?q=abcdef"})

    @patch("UrlShortener.src.routes.api_routes.search_doc_by_long_url")
    @patch("UrlShortener.src.routes.api_routes.save_doc")
    @patch("UrlShortener.src.routes.api_routes.remove_expired_urls")
    @patch("UrlShortener.src.routes.api_routes.URLMapSchema")
    def test_shorten_url_existing(
        self,
        mock_URLMapSchema,
        mock_remove_expired_urls,
        mock_save_doc,
        mock_search_doc_by_long_url,
    ):
        mock_URLMapSchema.return_value = MagicMock(
            long_url="http://example.com",
            code="abcdef",
            model_dump=MagicMock(),
            extend_expiration=MagicMock(),
        )
        mock_search_doc_by_long_url.return_value = MagicMock(
            to_dict=MagicMock(
                return_value={"long_url": "http://example.com", "code": "abcdef"}
            )
        )
        response = client.post("/api/shorten", json={"url": "http://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"url": "http://testserver/?q=abcdef"})

    @patch("UrlShortener.src.routes.api_routes.search_doc_by_code")
    @patch("UrlShortener.src.routes.api_routes.URLMapSchema")
    def test_redirect_url(self, mock_URLMapSchema, mock_search_doc_by_code):
        mock_search_doc_by_code.return_value = MagicMock()
        mock_URLMapSchema.return_value = MagicMock(
            long_url="http://example.com", extend_expiration=MagicMock()
        )
        response = client.get("/?q=abcdef")
        self.assertEqual(response.url, "http://example.com")

    @patch("UrlShortener.src.routes.api_routes.search_doc_by_code")
    def test_redirect_url_not_found(self, mock_search_doc_by_code):
        mock_search_doc_by_code.side_effect = KeyError
        response = client.get("/?q=abcdef")
        self.assertEqual(response.status_code, 404)
