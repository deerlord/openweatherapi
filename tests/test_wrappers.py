import asyncio
from unittest import TestCase

from openweathermap import exceptions
from openweathermap.wrappers import model_return
from tests.fixtures.wrappers import EXAMPLE_MODEL_DICT, ExampleModel


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
        self.assertDictEqual(result.dict(), EXAMPLE_MODEL_DICT, "Incorrect dictionary returned")

    def test_time_cache(self):
        # not sure how to test
        pass

    def test_convert_dict_validation_failure(self):
        @model_return(model=ExampleModel)
        async def func():
            return {"bad": "value"}

        with self.assertLogs("") as cm:
            self.assertRaises(exceptions.ResponseMalformed, asyncio.run, func())
        test_log = [
            "ERROR:root:Unable to parse ExampleModel body - 2 validation errors for "
            "ExampleModel\n"
            "key_one\n"
            "  field required (type=value_error.missing)\n"
            "key_two\n"
            "  field required (type=value_error.missing)\n"
            "Called with arguments: {'bad': 'value'}"
        ]
        self.assertEqual(cm.output, test_log)

    def test_convert_list_validation_failure(self):
        @model_return(model=ExampleModel)
        async def func():
            return [{"key_one": "value", "key_two": "value"}, {"bad": "value"}]

        with self.assertLogs("") as cm:
            self.assertRaises(exceptions.ResponseMalformed, asyncio.run, func())
        test_log = [
            "ERROR:root:Unable to parse ExampleModel body - 2 validation errors for "
            "ExampleModel\n"
            "key_one\n"
            "  field required (type=value_error.missing)\n"
            "key_two\n"
            "  field required (type=value_error.missing)\n"
            "Called with arguments: {'bad': 'value'}"
        ]
        self.assertEqual(cm.output, test_log, "Error not logged correctly")
