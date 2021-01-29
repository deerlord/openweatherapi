class OpenWeatherAPIException(BaseException):
    pass


class NoCoordinates(OpenWeatherAPIException):
    pass


class ResponseMalformed(OpenWeatherAPIException):
    pass


class IconNotFound(OpenWeatherAPIException):
    pass


class BadRequest(OpenWeatherAPIException):
    pass
