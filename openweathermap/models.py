from typing import List

from pydantic import BaseModel


class WeatherDataBaseModel(BaseModel):
    dt: int

    def data(self):
        return self.dict(exclude="dt")

    def flatten(self):
        data = self.dict()
        dict_fields = [
            field for field, value in data.items() if isinstance(value, dict)
        ]
        for field in dict_fields:
            flat = self._flatten_dict(field)
            data.pop(field)
            data.update(flat)
        return data

    def _flatten_dict(self, field: str):
        return {
            f"{field}_{key}": value for key, value in getattr(self, field, {}).items()
        }


class Weather(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class Hourly(WeatherDataBaseModel):
    temp: float
    feels_like: float
    pressure: float
    humidity: float
    dew_point: float
    clouds: float
    visibility: int
    wind_speed: float
    wind_deg: int
    weather: List[Weather]
    pop: float
    rain: dict = {"1h": 0.0}
    snow: dict = {"1h": 0.0}


class Current(WeatherDataBaseModel):
    sunrise: int
    sunset: int
    temp: float
    feels_like: float
    pressure: float
    humidity: float
    uvi: float
    clouds: float
    visibility: int
    wind_speed: float
    wind_deg: int
    weather: List[Weather]
    rain: dict = {"1h": 0.0}
    snow: dict = {"1h": 0.0}

    def weather_ids(self):
        for weather in self.weather:
            yield weather.id


class Minutely(WeatherDataBaseModel):
    precipitation: float


class DailyTemp(BaseModel):
    day: float
    min: float
    max: float
    night: float
    eve: float
    morn: float


class DailyFeelsLike(BaseModel):
    day: float
    night: float
    eve: float
    morn: float


class Daily(WeatherDataBaseModel):
    sunrise: int
    sunset: int
    temp: DailyTemp
    feels_like: DailyFeelsLike
    pressure: float
    humidity: float
    dew_point: float
    wind_speed: float
    wind_deg: int
    weather: List[Weather]
    clouds: float
    pop: float
    rain: float = 0.0
    uvi: float = 0.0


class Alert(BaseModel):
    sender_name: str
    event: str
    start: int
    end: int
    description: str


class OneCallAPIResponse(BaseModel):
    lat: float
    lon: float
    timezone: str
    timezone_offset: int
    current: Current
    minutely: List[Minutely] = []
    hourly: List[Hourly] = []
    daily: List[Daily] = []
    alerts: List[Alert] = []

{
  "coord":[
    50,
    50
  ],
  "list":[
    {
      "dt":1605182400,
      "main":{
        "aqi":1
      },
      "components":{
        "co":201.94053649902344,
        "no":0.01877197064459324,
        "no2":0.7711350917816162,
        "o3":68.66455078125,
        "so2":0.6407499313354492,
        "pm2_5":0.5,
        "pm10":0.540438711643219,
        "nh3":0.12369127571582794
      }
    }
  ]
}


class AirPollutionComponents(BaseModel):
    co: float
    no: float
    no2: float
    o3: float
    so2: float
    pm2_5: float
    pm10: float
    nh3: float


class AirPollution(BaseModel):
    dt: int
    main: dict
    components: AirPollutionComponents


class AirPollutionAPIResponse(BaseModel):
    coord: list
    list: AirPollution
