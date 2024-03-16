import asyncio
import unittest
from unittest.mock import MagicMock, patch

from fastapi.datastructures import URL

from UrlShortener.src.db import (
    LongURL,
    ShortURL,
    fetch_redirect_url,
    generate_shorten_url,
)

# class TestURLShortener(unittest.TestCase):

#     @patch("UrlShortener.src.shortener.db.collection")
#     @patch("UrlShortener.src.shortener.generate_short_code")
#     def test_generate_shorten_url(self, mock_generate_short_code, mock_db_collection):
#         mock_generate_short_code.return_value = "abcdef"
#         mock_db_collection.return_value.document.return_value.set.return_value = None
#         long_url = LongURL(url="http://example.com")
#         result = asyncio.run(generate_shorten_url(URL("http://short.com/"), long_url))
#         self.assertEqual(result.url, "http://short.com/abcdef")

#     @patch("UrlShortener.src.shortener.db.collection")
#     def test_fetch_redirect_url(self, mock_db_collection):
#         mock_doc = MagicMock()
#         mock_doc.exists = True
#         mock_doc.to_dict.return_value = {"long_url": "http://example.com/"}
#         mock_db_collection.return_value.document.return_value.get.return_value = (
#             mock_doc
#         )
#         result = asyncio.run(fetch_redirect_url("abcdef"))
#         self.assertEqual(result.url, "http://example.com/")

#     @patch("UrlShortener.src.shortener.db.collection")
#     def test_fetch_redirect_url_not_found(self, mock_db_collection):
#         mock_doc = MagicMock()
#         mock_doc.exists = False
#         mock_db_collection.return_value.document.return_value.get.return_value = (
#             mock_doc
#         )
#         with self.assertRaises(KeyError):
#             asyncio.run(fetch_redirect_url("abcdef"))

class TestURLShortener(unittest.TestCase):

    @patch("UrlShortener.src.shortener.url_collection.where")
    def test_generate_shorten_url(self, mock_where):
        mock_query = MagicMock()
        mock_query.__len__.return_value = 0
        mock_where.return_value.limit.return_value.get.return_value = mock_query
        long_url = LongURL(url="http://example.com")
        result = asyncio.run(generate_shorten_url("http://short.com/", long_url))
        self.assertIsInstance(result, ShortURL)

    @patch("UrlShortener.src.shortener.url_collection.document")
    def test_fetch_redirect_url(self, mock_document):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"long_url": "http://example.com/"}
        mock_document.return_value.get.return_value = mock_doc
        result = asyncio.run(fetch_redirect_url("abcdef"))
        self.assertEqual(result.url, "http://example.com/")

    @patch("UrlShortener.src.shortener.url_collection.document")
    def test_fetch_redirect_url_not_found(self, mock_document):
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_document.return_value.get.return_value = mock_doc
        with self.assertRaises(KeyError):
            asyncio.run(fetch_redirect_url("abcdef"))


if __name__ == "__main__":
    unittest.main()
