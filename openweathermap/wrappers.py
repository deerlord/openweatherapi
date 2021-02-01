import logging
from functools import wraps
from typing import Any, Dict, List, Type

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from openweathermap import exceptions


def model_return(model: Type[BaseModel]):
    def wrapper(func):
        @wraps(func)
        async def caller(*args, **kwargs):
            result = await func(*args, **kwargs)
            return CONVERTERS[type(result)](model=model, data=result)

        return caller

    return wrapper


def convert_list(model: Type[BaseModel], data: List[Dict[str, Any]]) -> List[BaseModel]:
    result = []
    for d in data:
        try:
            m = model(**d)
            result.append(m)
        except PydanticValidationError as error:
            message = (
                f"Unable to parse {model.__name__} body - {error}"
                f"\nCalled with arguments: {d}"
            )
            logging.error(message)
            raise exceptions.ResponseMalformed()
    return result


def convert_dict(model: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    try:
        return model(**data)
    except PydanticValidationError as error:
        message = (
            f"Unable to parse {model.__name__} body - {error}"
            f"\nCalled with arguments: {data}"
        )
        logging.error(message)
        raise exceptions.ResponseMalformed()


CONVERTERS = {list: convert_list, dict: convert_dict}
