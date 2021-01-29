from unittest import TestCase

from openweathermap import wrappers

from tests.fixtures.wrappers import ExampleModel, EXAMPLE_MODEL_DICT
import asyncio
from openweathermap.wrappers import model_return



class TestWrappers(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_model_return(self):
        @model_return(model=ExampleModel)
        async def func():
            return EXAMPLE_MODEL_DICT

        result = asyncio.run(func())
        self.assertDictEqual(
            result.dict(),
            EXAMPLE_MODEL_DICT,
            'Incorrect dictionary returned'
        )

