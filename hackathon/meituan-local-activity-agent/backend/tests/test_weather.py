import pytest
from unittest.mock import patch
from tools.weather import get_weather, _weather_code_to_zh


class TestWeatherCodeMapping:
    def test_clear_sky(self):
        assert _weather_code_to_zh(0) == "晴"

    def test_rain(self):
        assert _weather_code_to_zh(65) == "雨"

    def test_thunderstorm(self):
        assert _weather_code_to_zh(99) == "雷暴"

    def test_unknown(self):
        assert _weather_code_to_zh(999) == "未知"


class TestGetWeatherMockFallback:
    @patch("tools.weather.config.USE_REAL_APIS", False)
    def test_fallback_to_mock(self):
        result = get_weather("上海", "2026-05-20")
        assert result["city"] == "上海"
        assert "°C" in result.get("temperature", "")

    @patch("tools.weather.config.USE_REAL_APIS", True)
    @patch("tools.weather._real_get_weather", side_effect=Exception("API down"))
    def test_real_fails_then_fallback(self, mock_real):
        result = get_weather("北京")
        assert result["city"] == "北京"
