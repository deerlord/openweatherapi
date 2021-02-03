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

    def test_json_request(self):
        with responses() as resps:
            resps.get("/", status=200, payload={'KEY': 'VALUE'})
            result = asyncio.run(self.client._json_request(url=""))
        self.assertEqual(
            result,
            {'KEY': 'VALUE'},
            'Did not return  expected JSON.'
        )

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
            resps.get("/", status=200, payload='VALUE')
            result = asyncio.run(self.client._binary_request(url="", params={}))
        self.assertEqual(
            result,
            b'"VALUE"',
            'Did not return expected byte string.'
        )
    
    def test_binary_request_error(self):
        with responses() as resps:
             resps.get('/', status=500, payload='')
             with self.assertLogs("", level="ERROR") as cm:
                 self.assertRaises(
                    exceptions.BadRequest,
                    asyncio.run,
                    self.client._binary_request(url="")
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


class TestOpenWeatherGeocoding(TestCase):
    def setUp(self):
        self.client = api.OpenWeatherGeocoding(appid="")

    def test_geocode(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/geo/1.0/direct?limit=2&q=London%252CTX%252CGB",
                status=200,
                payload=fixtures.GEOCODE_API_RESPONSE
            )
            result = asyncio.run(self.client.geocode(city='London', state='TX', country='GB', limit=2))
        print('??', result)
        # test result
