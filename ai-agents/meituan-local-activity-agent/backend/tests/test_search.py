import pytest
from unittest.mock import patch
from tools.search import search_poi


import json
from unittest.mock import patch, MagicMock

from tools.search import search_poi, _cached_search


class TestSearchFallback:
    @patch("tools.search.config.USE_REAL_APIS", False)
    def test_fallback_to_mock(self):
        results = search_poi("咖啡", "上海")
        assert isinstance(results, list)
        if results:
            assert "name" in results[0]

    @patch("tools.search.config.USE_REAL_APIS", True)
    @patch("tools.search._real_search_poi", side_effect=Exception("API down"))
    def test_real_fails_then_fallback(self, mock_real):
        results = search_poi("火锅", "成都")
        assert isinstance(results, list)


class TestSearchCache:
    @patch("tools.search._rate_limited_call")
    def test_cache_hits(self, mock_call):
        mock_call.return_value = [{"display_name": "测试", "lat": "30", "lon": "120", "type": "cafe"}]
        r1 = _cached_search("咖啡", "上海")
        r2 = _cached_search("咖啡", "上海")
        mock_call.assert_called_once()
        assert json.loads(r1)[0]["display_name"] == "测试"
