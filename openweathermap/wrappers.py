import logging
from functools import wraps

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError as PydanticValidationError


def model_return(model: BaseModel):
    # take in base model
    # run results from method through mode
    # raise/log if exception
    def wrapper(func):
        @wraps(func)
        async def caller(*args, **kwargs):
            result = await func(*args, **kwargs)
            if not isinstance(result, dict):
                raise exceptions
            try:
                response = model(**result)
            except PydanticValidationError as error:
                message = (
                    f"Error: Unable to parse {model.__name__} body - {error}"
                    f"\nCalled with arguments: {result}"
                )
                logging.error(message)
                raise exceptions.ResponseMalformed()
            return response

        return caller

    return wrapper
