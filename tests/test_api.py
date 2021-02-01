import asyncio
import pytest

from unittest import TestCase

from aioresponses import aioresponses as responses  # type: ignore

from openweathermap import api, exceptions
from tests.fixtures import openweatherapi as fixtures


@pytest.fixture
def event_loop():
    loop = MyCustomLoop()
    yield loop
    loop.close()


class TestBaseAPI(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherBase(appid="")

    def test_api_request(self):
        with responses() as resps:
            resps.get("/", status=200, payload={})
            asyncio.run(self.client._json_request(url="", params={}))

    def test_api_request_error(self):
        with responses() as resps:
            resps.get("/", status=500, payload={})
            with self.assertLogs("", level="ERROR") as cm:
                self.assertRaises(
                    exceptions.BadRequest,
                    asyncio.run,
                    self.client._json_request(url="", params={}),
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
        self.client = api.OpenWeatherData(appid="")

    def test_one_call(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/"
                "onecall?lat=0.0&lon=0.0&units=imperial",
                payload=fixtures.ONE_CALL_API_RESPONSE_INPUT,
                status=200,
            )
            result = asyncio.run(self.client.one_call(lat=0.0,lon=0.0,units='imperial'))
        self.assertDictEqual(result.dict(), fixtures.ONE_CALL_API_AS_DICT)


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
                #response = asyncio.run(getattr(self.client, layer))
                func = getattr(self.client, layer)
                result = asyncio.run(func(0,0,0))
            results.append(result)
        self.assertEqual(
            results,
            [b'', b'', b'', b'', b'']
        )
