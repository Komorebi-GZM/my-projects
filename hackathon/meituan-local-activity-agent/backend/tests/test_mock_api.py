"""mock_api 单元测试。"""
import os
import random

from unittest import mock
from tools import mock_api


def test_mock_book_poi_success():
    random.seed(42)
    with mock.patch.object(mock_api.config, "MOCK_HIGH_PRIORITY_RATE", 1.0):
        result = mock_api.mock_book_poi(poi_name="海底捞", trace_id="test_001")
    assert result["success"] is True
    assert "booking_id" in result


def test_mock_book_poi_failure():
    random.seed(42)
    with mock.patch.object(mock_api.config, "MOCK_HIGH_PRIORITY_RATE", 0.0):
        result = mock_api.mock_book_poi(poi_name="海底捞", trace_id="test_001")
    assert result["success"] is False
    assert "error" in result


def test_mock_search_poi_failure_fallback():
    random.seed(42)
    with mock.patch.object(mock_api.config, "MOCK_HIGH_PRIORITY_RATE", 0.0):
        result = mock_api.mock_search_poi(keyword="火锅", trace_id="test_001")
    assert result == []
