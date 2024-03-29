import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from UrlShortener.src.api import app

client = TestClient(app)


class TestShortenURL(unittest.TestCase):

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
        self.assertEqual(response.json(), {"url": "http://testserver/abcdef"})

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
        self.assertEqual(response.json(), {"url": "http://testserver/abcdef"})

    @patch("UrlShortener.src.routes.api_routes.handle_custom_code")
    @patch("UrlShortener.src.routes.api_routes.handle_standard_code")
    def test_shorten_url_with_custom_code(
        self, mock_handle_standard_code, mock_handle_custom_code
    ):
        mock_handle_custom_code.return_value = MagicMock(code="custom")
        response = client.post(
            "/api/shorten", json={"url": "http://example.com", "code": "custom"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"url": "http://testserver/custom"})
        mock_handle_custom_code.assert_called_once()
        mock_handle_standard_code.assert_not_called()

    @patch("UrlShortener.src.routes.api_routes.handle_custom_code")
    @patch("UrlShortener.src.routes.api_routes.handle_standard_code")
    def test_shorten_url_with_existing_code(
        self, mock_handle_standard_code, mock_handle_custom_code
    ):
        mock_handle_custom_code.side_effect = HTTPException(
            status_code=400, detail="Code already exists"
        )
        response = client.post(
            "/api/shorten", json={"url": "http://example.com", "code": "existing"}
        )
        self.assertEqual(response.status_code, 400)
        mock_handle_custom_code.assert_called_once()
        mock_handle_standard_code.assert_not_called()

    @patch("UrlShortener.src.routes.api_routes.handle_custom_code")
    @patch("UrlShortener.src.routes.api_routes.handle_standard_code")
    def test_shorten_url_without_custom_code(
        self, mock_handle_standard_code, mock_handle_custom_code
    ):
        mock_handle_standard_code.return_value = MagicMock(code="abcdef")
        response = client.post("/api/shorten", json={"url": "http://example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"url": "http://testserver/abcdef"})
        mock_handle_standard_code.assert_called_once()
        mock_handle_custom_code.assert_not_called()


class TestURLRedirect(unittest.TestCase):
    @patch("UrlShortener.src.routes.api_routes.search_doc_by_code")
    @patch("UrlShortener.src.routes.api_routes.URLMapSchema")
    def test_redirect_url(self, mock_URLMapSchema, mock_search_doc_by_code):
        mock_code = "q_abcdef"
        mock_long_url = "https://www.google.com"

        mock_search_doc_by_code.return_value = MagicMock(
            to_dict=MagicMock(
                return_value={
                    "long_url": mock_long_url,
                    "code": mock_code,
                    "expiration": datetime.now(),
                }
            )
        )
        mock_URLMapSchema.return_value = MagicMock(
            long_url=mock_long_url,
            extend_expiration=MagicMock(),
            code=mock_code,
        )

        response = client.get(f"/{mock_code}")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, mock_long_url)

    @patch("UrlShortener.src.routes.api_routes.search_doc_by_code")
    def test_redirect_url_not_found(self, mock_search_doc_by_code):
        mock_search_doc_by_code.side_effect = KeyError
        response = client.get("/q_abcdef")
        self.assertEqual(response.status_code, 404)
