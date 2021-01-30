import asyncio
from unittest import TestCase

from aioresponses import aioresponses as responses  # type: ignore

from openweathermap import api, exceptions
from tests.fixtures import openweatherapi as fixtures


class TestBaseAPI(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherBase(api_key="")

    def test_api_request(self):
        with responses() as resps:
            resps.get("/", status=200, payload={})
            asyncio.run(self.client._api_request(url="", params={}))

    def test_api_request_error(self):
        with responses() as resps:
            resps.get("/", status=500, payload={})
            with self.assertLogs("", level="ERROR") as cm:
                self.assertRaises(
                    exceptions.BadRequest,
                    asyncio.run,
                    self.client._api_request(url="", params={}),
                )
                self.assertEqual(cm.output, ["ERROR:root:/ returns 500"])

    def test_url_formatter(self):
        result = self.client._url_formatter(url="/test/url")
        self.assertEqual(result, "/test/url")

    def test_url_formatter_strip(self):
        result = self.client._url_formatter(url="test/url")
        self.assertEqual(result, "/test/url")


class TestOpenWeatherData(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherData(api_key="", lat=0.0, lon=0.0)

    def test_one_call(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/"
                "onecall?lat=0.0&lon=0.0&units=imperial",
                payload=fixtures.ONE_CALL_API_RESPONSE_INPUT,
                status=200,
            )
            result = asyncio.run(self.client.one_call())
        self.assertDictEqual(result.dict(), fixtures.ONE_CALL_API_AS_DICT)


class TestOpenWeatherMap(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherMap(api_key="", tile_x=0, tile_y=0, zoom=0)

    def test_attributes(self):
        results = []
        for layer in ["clouds", "precipitation", "pressure", "wind", "temp"]:
            with responses() as resps:
                resps.get(
                    f"https://tile.openweathermap.org/map/{layer}_new/0/0/0.png?appid=",
                    status=200,
                    payload={},
                )
                response = getattr(self.client, layer)
                results.append(response)
        print(results)
