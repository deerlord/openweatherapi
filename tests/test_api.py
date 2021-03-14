import asyncio
from unittest import TestCase

from aioresponses import aioresponses as responses  # type: ignore

from openweathermap import api, exceptions
from tests.fixtures import openweatherapi as fixtures


class TestBaseAPI(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherBase(appid="APPID")

    def test_json_request(self):
        with responses() as resps:
            resps.get("/", status=200, payload={"KEY": "VALUE"})
            result = asyncio.run(self.client._json_request(url=""))
        self.assertEqual(result, {"KEY": "VALUE"}, "Did not return  expected JSON.")

    def test_json_request_error(self):
        with responses() as resps:
            resps.get("/", status=500, payload={})
            with self.assertLogs("", level="ERROR") as cm:
                self.assertRaises(
                    exceptions.BadRequest,
                    asyncio.run,
                    self.client._json_request(url=""),
                )
        self.assertEqual(cm.output, ["ERROR:root:/ returned 500"])

    def test_binary_request(self):
        with responses() as resps:
            resps.get("/", status=200, payload="VALUE")
            result = asyncio.run(self.client._binary_request(url="", params={}))
        self.assertEqual(result, b'"VALUE"', "Did not return expected byte string.")

    def test_binary_request_error(self):
        with responses() as resps:
            resps.get("/", status=500, payload="")
            with self.assertLogs("", level="ERROR") as cm:
                self.assertRaises(
                    exceptions.BadRequest,
                    asyncio.run,
                    self.client._binary_request(url=""),
                )
        self.assertEqual(cm.output, ["ERROR:root:/ returned 500"])

    def test_url_formatter(self):
        result = self.client._url_formatter(url="/test/url")
        self.assertEqual(result, "/test/url")

    def test_url_formatter_strip(self):
        result = self.client._url_formatter(url="test/url")
        self.assertEqual(result, "/test/url")


class TestOpenWeatherData(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherData(appid="APPID")

    def test_one_call(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/" "onecall?appid=APPID&lat=0.0&lon=0.0&units=imperial",
                payload=fixtures.ONE_CALL_API_RESPONSE_INPUT,
                status=200,
            )
            result = asyncio.run(self.client.one_call(lat=0.0, lon=0.0, units="imperial"))
        self.assertDictEqual(
            result.dict(),
            fixtures.ONE_CALL_API_AS_DICT,
            "Model does not match API response",
        )

    def test_air_pollution(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/" "air_pollution?lat=0.0&lon=0.0&appid=APPID",
                payload=fixtures.AIR_POLLUTION_API_RESPONSE_INPUT,
                status=200,
            )
            result = asyncio.run(self.client.air_pollution(lat=0.0, lon=0.0))
        self.assertDictEqual(
            result.dict(),
            fixtures.AIR_POLLUTION_API_RESPONSE_INPUT,
            "Model does not match API response",
        )

    def test_air_pollution_forecast(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/air_pollution/" "forecast?appid=APPID&lat=0.0&lon=0.0",
                payload=fixtures.AIR_POLLUTION_FORECAST_API_RESPONSE,
                status=200,
            )
            result = asyncio.run(self.client.air_pollution_forecast(lat=0.0, lon=0.0))
        self.assertDictEqual(
            result.dict(),
            fixtures.AIR_POLLUTION_FORECAST_API_RESPONSE,
            "Model does  not match  API response",
        )

    def test_air_pollution_history(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/air_pollution/history?"
                "appid=APPID&end=2&lat=0.0&lon=0.0&start=1",
                payload=fixtures.AIR_POLLUTION_HISTORY_API_RESPONSE,
                status=200,
            )
            result = asyncio.run(self.client.air_pollution_history(lat=0.0, lon=0.0, start=1, end=2))
        self.assertDictEqual(
            result.dict(),
            fixtures.AIR_POLLUTION_HISTORY_API_RESPONSE,
            "Model does not match API response",
        )

    def test_uvi(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/uvi?" "appid=APPID&lat=0.0&lon=0.0",
                payload=fixtures.UVI_API_RESPONSE,
                status=200,
            )
            result = asyncio.run(self.client.uvi(lat=0.0, lon=0.0))
        self.assertDictEqual(
            result.dict(),
            fixtures.UVI_API_RESPONSE,
            "Model does not match API response",
        )

    def test_uvi_forecast(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/uvi/forecast?" "appid=APPID&cnt=8&lat=0.0&lon=0.0",
                payload=fixtures.UVI_FORECAST_API_RESPONSE,
                status=200,
            )
            result = asyncio.run(self.client.uvi_forecast(lat=0.0, lon=0.0, cnt=8))
        self.assertEqual(
            result,
            fixtures.UVI_FORECAST_API_RESPONSE,
            "Model did not match API response",
        )

    def test_uvi_history(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/uvi/history?"
                "appid=APPID&cnt=5&end=2&lat=0.0&lon=0.0&start=1",
                payload=fixtures.UVI_LIST_API_RESPONSE,
                status=200,
            )
            self.maxDiff = None
            result = asyncio.run(self.client.uvi_history(lat=0.0, lon=0.0, cnt=5, start=1, end=2))
        self.assertEqual(
            result,
            fixtures.UVI_LIST_API_RESPONSE,
            "Model does not match API response",
        )


class TestOpenWeatherMap(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherMap(appid="")

    def test_attributes(self):
        results = []
        for layer in ["clouds", "precipitation", "pressure", "wind", "temp"]:
            with responses() as resps:
                resps.get(
                    f"https://tile.openweathermap.org/map/{layer}_new/0/0/0.png?appid=",
                    status=200,
                )
                # response = asyncio.run(getattr(self.client, layer))
                func = getattr(self.client, layer)
                result = asyncio.run(func(0, 0, 0))
            results.append(result)
        self.assertEqual(results, [b"", b"", b"", b"", b""])


class TestOpenWeatherGeocoding(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherGeocoding(appid="APPID")

    def test_geocode(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/geo/1.0/direct?" "appid=APPID&limit=2&q=London%252CTX%252CGB",
                status=200,
                payload=fixtures.GEOCODE_API_RESPONSE,
            )
            result = asyncio.run(self.client.geocode(city="London", state="TX", country="GB", limit=2))

        results = [model.dict() for model in result]
        self.assertEqual(results, fixtures.GEOCODE_API_RESPONSE, "Model does not match API response")

    def test_reverse(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/geo/1.0/reverse?" "appid=APPID&lat=0.0&limit=5&lon=0.0",
                payload=fixtures.REVERSE_API_RESPONSE,
                status=200,
            )
            result = asyncio.run(self.client.reverse(lat=0.0, lon=0.0, limit=5))
        results = [model.dict() for model in result]
        self.maxDiff = None
        self.assertEqual(results, fixtures.REVERSE_API_RESPONSE, "Model does not match API response")


class TestUtilities(TestCase):
    def test_icon(self):
        with responses() as resps:
            resps.get(
                "http://openweathermap.org/img/wn/01d@2x.png",
                body=fixtures.ICON_BINARY,
                status=200,
            )
            result = asyncio.run(api.icon(icon_id="01d"))
        self.assertEqual(result, fixtures.ICON_BINARY, "Did not return expected binary data")
