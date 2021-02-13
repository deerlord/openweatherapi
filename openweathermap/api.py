import functools
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import aiohttp  # type: ignore

from openweathermap import exceptions, models, wrappers


@dataclass
class OpenWeatherBase:
    appid: str
    base_url = ""

    def _url_formatter(self, url: str) -> str:
        url = url[1:] if url.startswith("/") else url
        return f"{self.base_url}/{url}"

    async def _json_request(self, url: str, params: Dict[str, Any] = {}) -> Any:
        result = {}
        url = self._url_formatter(url)
        async with aiohttp.ClientSession() as session:
            async with (session.get(url=url, params=params)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                else:
                    message = f"{resp.url} returned {resp.status}"
                    logging.error(message)
                    raise exceptions.BadRequest(resp.status)
        return result

    async def _binary_request(self, url: str, params: Dict[str, Any] = {}) -> bytes:
        result = b""
        url = self._url_formatter(url=url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    result = await resp.read()
                else:
                    message = f"{resp.url} returned {resp.status}"
                    logging.error(message)
                    raise exceptions.BadRequest(resp.status)
        return result


@dataclass
class OpenWeatherData(OpenWeatherBase):
    """
    Documentation at: https://openweathermap.org/api/one-call-api
    """

    base_url = "https://api.openweathermap.org/data/2.5"

    async def _basic_request(self, url: str, lat: float, lon: float, **kwargs) -> Any:
        params = {"lat": lat, "lon": lon, "appid": self.appid}  # type: Dict[str, Any]
        params.update(**kwargs)
        return await self._json_request(url=url, params=params)

    @wrappers.model_return(model=models.OneCallAPIResponse)
    async def one_call(self, lat: float, lon: float, units: str) -> Dict[str, Any]:
        return await self._basic_request(url="/onecall", lat=lat, lon=lon, units=units)

    @wrappers.model_return(model=models.AirPollutionAPIResponse)
    async def air_pollution(self, lat: float, lon: float) -> Dict[str, Any]:
        return await self._basic_request(url="/air_pollution", lat=lat, lon=lon)

    @wrappers.model_return(model=models.AirPollutionAPIResponse)
    async def air_pollution_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        return await self._basic_request(
            url="/air_pollution/forecast", lat=lat, lon=lon
        )

    @wrappers.model_return(model=models.AirPollutionAPIResponse)
    async def air_pollution_history(
        self, lon: float, lat: float, start: int, end: int
    ) -> Dict[str, Any]:
        return await self._basic_request(
            url="/air_pollution/history", lat=lat, lon=lon, start=start, end=end
        )

    @wrappers.model_return(model=models.UviAPIResponse)
    async def uvi(self, lat: float, lon: float) -> Dict[str, Any]:
        return await self._basic_request(url="/uvi", lat=lat, lon=lon)

    @wrappers.model_return(model=models.UviAPIResponse)
    async def uvi_forecast(
        self, lat: float, lon: float, cnt: int
    ) -> List[Dict[str, Any]]:
        return await self._basic_request(url="/uvi/forecast", lat=lat, lon=lon, cnt=cnt)

    @wrappers.model_return(model=models.UviAPIResponse)
    async def uvi_history(
        self, lat: float, lon: float, cnt: int, start: int, end: int
    ) -> List[Dict[str, Any]]:
        return await self._basic_request(
            url="/uvi/history", lat=lat, lon=lon, cnt=cnt, start=start, end=end
        )


@dataclass
class OpenWeatherMap(OpenWeatherBase):
    """
    Documentation at: https://openweathermap.org/api/weathermaps
    """

    base_url = "https://tile.openweathermap.org/map"

    async def _basic_request(self, layer: str, x: int, y: int, z: int) -> bytes:
        url = f"/{layer}/{z}/{x}/{y}.png"
        return await self._binary_request(url=url, params={"appid": self.appid})

    def __getattribute__(self, attr) -> Any:
        # enables map endpoints to accessed without repetitive code
        # for instance: map = self.clouds(x,y,z)
        if attr in ["clouds", "precipitation", "pressure", "wind", "temp"]:
            # returns a callable coro
            return functools.partial(self._basic_request, f"{attr}_new")
        return super().__getattribute__(attr)


class OpenWeatherGeocoding(OpenWeatherBase):

    base_url = "https://api.openweathermap.org/geo/1.0"

    @wrappers.model_return(model=models.GeocodingAPIResponse)
    async def geocode(
        self, city: str, state: str, country: str, limit: int = None
    ) -> List[Dict[str, Any]]:
        params = {
            "appid": self.appid,
            "q": f"{city},{state},{country}",
        }  # type: Dict[str, Any]
        if limit:
            params.update({"limit": limit})
        return await self._json_request(url="/direct", params=params)

    @wrappers.model_return(model=models.GeocodingAPIResponse)
    async def reverse(
        self, lat: float, lon: float, limit: int = None
    ) -> List[Dict[str, Any]]:
        params = {"lat": lat, "lon": lon, "appid": self.appid}  # type: Dict[str, Any]
        if limit:
            params.update({"limit": limit})
        return await self._json_request(url="/reverse", params=params)


async def icon(icon_id: str) -> bytes:
    client = OpenWeatherBase(appid="")
    client.base_url = "http://openweathermap.org/img/wn"
    url = f"/{icon_id}@2x.png"
    return await client._binary_request(url=url)
