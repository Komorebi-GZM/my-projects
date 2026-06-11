import pytest
import re
from unittest.mock import patch
from tools.booking import _generate_booking_id, _time_based_success_rate, _get_city_pool, book_poi


class TestBookingId:
    def test_format(self):
        bid = _generate_booking_id("上海")
        assert re.match(r"^[A-Z]+_\d{8}_[a-f0-9]{6}$", bid)

    def test_city_code_bj(self):
        assert _generate_booking_id("北京").startswith("BJ_")


class TestCityPool:
    def test_shanghai_pool(self):
        pool = _get_city_pool("上海")
        assert "武康路老洋房" in pool

    def test_fallback_pool(self):
        pool = _get_city_pool("未知城市")
        assert pool == ["热门咖啡馆", "网红餐厅", "城市公园", "购物中心", "艺术展览馆"]


class TestBookPoi:
    def test_success_returns_booking_id(self):
        result = book_poi("测试餐厅", "14:00-15:00", city="上海")
        if result["success"]:
            assert "booking_id" in result
            assert result["booking_id"].startswith("SH_")

    def test_failure_returns_error(self):
        with patch("tools.booking.random.random", return_value=1.0):
            result = book_poi("测试餐厅", "18:00-20:00", city="上海")
            assert not result["success"]
            assert "error" in result


class TestTimeBasedRate:
    def test_dinner_rush(self):
        assert _time_based_success_rate("18:00-20:00") == 0.70

    def test_lunch_rush(self):
        assert _time_based_success_rate("12:00-13:30") == 0.80

    def test_normal(self):
        assert _time_based_success_rate("10:00-11:00") == 0.90

    def test_no_time_slot(self):
        assert _time_based_success_rate(None) == 0.90
