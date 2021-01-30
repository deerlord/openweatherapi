import logging
from dataclasses import dataclass, field

import aiohttp  # type: ignore
import asyncio
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from openweathermap import exceptions, models, wrappers


# TESTED
@dataclass
class OpenWeatherBase:
    api_key: str
    base_url = ""

    def _url_formatter(self, url: str) -> str:
        url = url[1:] if url.startswith("/") else url
        result = f"{self.base_url}/{url}"
        return result

    async def _api_request(self, url: str, params: dict = {}) -> dict:
        result = {}
        async with aiohttp.ClientSession() as session:
            async with (session.get(self._url_formatter(url), params=params)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                else:
                    message = f"{resp.url} returns {resp.status}"
                    logging.error(message)
                    raise exceptions.BadRequest(resp.status)
        return result


# NEED TESTS
@dataclass
class OpenWeatherData(OpenWeatherBase):
    """
    Documentation at: https://openweathermap.org/api/one-call-api
    """

    api_key: str
    lat: float
    lon: float
    __units: str = field(init=False, default="imperial")
    base_url = "https://api.openweathermap.org/data/2.5"

    # NOT TESTED
    @property
    def params(self):
        return {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.api_key,
            "units": self.units,
        }

    @property
    def units(self) -> str:
        return self.__units

    @units.setter
    def units(self, value):
        if value.lower() in ["standard", "metric", "imperial"]:
            self.__units = value.lower()

    # TESTED
    @wrappers.model_return(model=models.OneCallAPIResponse)
    async def one_call(self):
        result = await self._api_request(url="onecall", params=self.params)
        return result

    # NOT TESTED
    @wrappers.model_return(model=models.AirPollutionAPIResponse)
    async def air_pollution(self):
        result = await self._api_request(url="air_pollution", params=self.params)
        return result

    @wrappers.model_return(model=models.AirPollutionAPIResponse)
    async def air_pollution_forecast(self):
        result = await self._api_request(url="", params=self.params)
        return result


@dataclass
class OpenWeatherMap(OpenWeatherBase):
    """
    Documentation at: https://openweathermap.org/api/weathermaps
    """
    base_url = "https://tile.openweathermap.org/map"
    tile_x: int
    tile_y: int
    zoom: int

    # NOT TESTED
    async def _basic_request(self, layer: str, x: int, y: int, z: int):
        url = f"/{layer}/{z}/{x}/{y}.png"
        result = await self._api_request(url=url, params={"appid": self.api_key})
        return result

    # NOT TESTED
    async def zoom_in(self):
        self.zoom = min(self.zoom + 1, OPENWEATHERMAP_MAX_ZOOM)

    # NOT TESTED
    async def zoom_out(self):
        self.zoom -= max(self.zoom - 1, 0)

    # partially tested, needs fallback
    def __getattribute__(self, attr):
        # enables map endpoints to accessed without repetitive code
        if attr in ["clouds", "precipitation", "pressure", "wind", "temp"]:
            result = asyncio.run(self._basic_request(
                layer=f"{attr}_new", x=self.tile_x, y=self.tile_x, z=self.zoom
            ))
            # possibly needs model
        else:
            return super().__getattribute__(attr) 
        return result


async def icon(self, icon_id: str) -> bytes:
    result = b""
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


OPENWEATHER_MAX_ZOOM = 50  # maybe not accurate
