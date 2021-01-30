from pydantic import BaseModel


class ExampleModel(BaseModel):
    key_one: str
    key_two: str


EXAMPLE_MODEL_DICT = {"key_one": "value_one", "key_two": "value_two"}
