from unittest import TestCase

from openweathermap import models
from tests.fixtures.openweatherapi import ONE_CALL_API_RESPONSE_INPUT


class TestModels(TestCase):
    def test_current_weather_ids(self):
        model = models.Current(**ONE_CALL_API_RESPONSE_INPUT["current"])
        result = [i for i in model.weather_ids()]
        self.assertEqual(result, [501, 201], "Did not get expected list of IDs.")
