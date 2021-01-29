import logging
from dataclasses import dataclass, field

import aiohttp  # type: ignore
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from openweathermap import exceptions, models, wrappers


@dataclass
class OpenWeatherClient:
    api_key: str
    lat: float
    lon: float
    version: str = "2.5"
    __units: str = field(init=False, default="imperial")

    def __post_init__(self):
        self._base_url = f"https://api.openweathermap.org/data/{self.version}"

    def set_location(self, latitude: str, longitude: str):
        self.lat = latitude
        self.lon = longitude

    @property
    def units(self) -> str:
        return self.__units

    @units.setter
    def units(self, value):
        if value.lower() in ["standard", "metric", "imperial"]:
            self.__units = value.lower()

    def _url_formatter(self, url: str) -> str:
        url = url[1:] if url.startswith("/") else url
        return f"{self._base_url}/{url}"

    async def _api_request(
        self,
        url: str,
        params: dict = {},
    ) -> dict:
        result = {}
        params.update({"appid": self.api_key, "units": self.units})
        async with aiohttp.ClientSession() as session:
            async with (session.get(self._url_formatter(url), params=params)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                else:
                    message = f"{resp.url} returned {resp.status}"
                    logging.error(message)
                    raise exceptions.BadRequest(resp.status)
        return result

    @wrappers.model_return(model=models.OneCallAPIResponse)
    async def one_call(self):
        result = await self._api_request(
            url="onecall", params={"lat": self.lat, "lon": self.lon}
        )
        return result

    async def one_call_old(self) -> models.OneCallAPIResponse:
        """
        Returns a full response for the One Call endpoint

        Raises openweatherapi.exceptions.ResponseMalformed
        """
        result = await self._api_request(
            url="onecall", params={"lat": self.lat, "lon": self.lon}
        )
        try:
            response = models.OneCallAPIResponse(**result)
        except PydanticValidationError as error:
            message = (
                f"Error: Unable to parse One Call API body - {error}"
                f"\nCalled with arguments: {result}"
            )
            logging.error(message)
            raise exceptions.ResponseMalformed()
        return response

    async def air_pollution(self):
        result = await self._api_request(
            url="air_pollution", params={"lat": self.lat, "lon": self.lon}
        )
        try:
            response = models.AirPollutionResponse(**result)
        except PydanticValidationError as error:
            message = (
                f"Error: Unable to parse One Call API body - {error}"
                f"\nCalled with arguments: {result}"
            )
            logging.error(message)
            raise exceptions.ResponseMalformed()

    async def icon(self, icon_id: str) -> bytes:
        result = None
        url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.read()
                else:
                    message = f"{resp.url} returned {resp.status}"
                    logging.error(message)
                    raise exceptions.IconNotFound()
        return result
