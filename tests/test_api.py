# testing tools
import asyncio
import unittest

from aioresponses import aioresponses as responses  # type: ignore

from openweathermap import api, exceptions, models
from tests.fixtures import openweatherapi as fixtures


class TestModels(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one_call(self):
        data = models.OneCallAPIResponse(**fixtures.ONE_CALL_API_RESPONSE_INPUT)
        self.assertDictEqual(data.dict(), fixtures.ONE_CALL_API_AS_DICT)

    def test_flatten_dict(self):
        model = models.Hourly(
            dt=123456,
            temp=0.0,
            feels_like=0.0,
            pressure=0.0,
            humidity=0.0,
            dew_point=0.0,
            clouds=0.0,
            visibility=0.0,
            wind_speed=0.0,
            wind_deg=0,
            weather=[],
            pop=0.0,
        )
        result = model._flatten_dict("rain")
        self.assertDictEqual(result, {"rain_1h": 0.0})

    def test_flatten(self):
        model = models.Hourly(
            dt=123456,
            temp=0.0,
            feels_like=0.0,
            pressure=0.0,
            humidity=0.0,
            dew_point=0.0,
            clouds=0.0,
            visibility=0.0,
            wind_speed=0.0,
            wind_deg=0,
            weather=[],
            pop=0.0,
        )
        result = model.flatten()
        self.assertDictEqual(result, fixtures.FLATTEN_HOURLY)

    def test_weather_ids(self):
        data = models.OneCallAPIResponse(**fixtures.ONE_CALL_API_RESPONSE_INPUT)
        self.assertEqual([x for x in data.current.weather_ids()], [501, 201])


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = api.OpenWeatherClient("", 0.0, 0.0)

    def tearDown(self):
        pass

    def test_api_request_error(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/?units=imperial",
                payload={},
                status=500,
            )
            self.assertRaises(
                exceptions.BadRequest,
                asyncio.run,
                self.client._api_request(url="")
            )
        #self.assertDictEqual(result, {})

    def test_units(self):
        self.client.units = "METRIC"
        self.assertEqual(self.client.units, "metric")

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

    def test_one_call_response_malformed(self):
        with responses() as resps:
            resps.get(
                "https://api.openweathermap.org/data/2.5/"
                "onecall?lat=0.0&lon=0.0&units=imperial",
                payload={},
                status=200,
            )
            with self.assertRaises(exceptions.ResponseMalformed):
                asyncio.run(self.client.one_call())

    def test_icon(self):
        with responses() as resps:
            resps.get(
                "http://openweathermap.org/img/wn/01d@2x.png",
                body=fixtures.ICON_BINARY,
                status=200,
            )
            result = asyncio.run(self.client.icon("01d"))
        self.assertEqual(result, fixtures.ICON_BINARY)

    def test_icon_error(self):
        with responses() as resps:
            resps.get(
                "http://openweathermap.org/img/wn/01d@2x.png",
                body=fixtures.ICON_BINARY,
                status=404,
            )
            with self.assertRaises(exceptions.IconNotFound):
                asyncio.run(self.client.icon("01d"))
