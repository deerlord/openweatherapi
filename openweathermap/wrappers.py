import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Type

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from openweathermap import exceptions


def model_return(model: Type[BaseModel]):
    def wrapper(func: Callable):
        @wraps(func)
        async def caller(*args, **kwargs):
            result = await func(*args, **kwargs)
            return CONVERTERS[type(result)](model=model, data=result)

        return caller

    return wrapper


def time_cache(func: Callable):
    cache = {}  # type: Dict[str, Any]

    @wraps(func)
    async def caller(self, *args, **kwargs):
        interval = timedelta(seconds=self.cache_interval)
        arg_sig = f"{args},{kwargs}"
        if arg_sig not in cache or (cache[arg_sig]["updated"] + interval) < datetime.utcnow():
            data = await func(self, *args, **kwargs)
            cache[arg_sig] = {"updated": datetime.utcnow(), "data": data}
        return cache[arg_sig]["data"]

    return caller


def convert_list(model: Type[BaseModel], data: List[Dict[str, Any]]) -> List[BaseModel]:
    result = []
    for d in data:
        try:
            m = model(**d)
            result.append(m)
        except PydanticValidationError as error:
            message = f"Unable to parse {model.__name__} body - {error}" f"\nCalled with arguments: {d}"
            logging.error(message)
            raise exceptions.ResponseMalformed()
    return result


def convert_dict(model: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    try:
        return model(**data)
    except PydanticValidationError as error:
        message = f"Unable to parse {model.__name__} body - {error}" f"\nCalled with arguments: {data}"
        logging.error(message)
        raise exceptions.ResponseMalformed()


CONVERTERS = {list: convert_list, dict: convert_dict}
