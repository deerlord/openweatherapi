from openweathermap import api
import asyncio

client = api.OpenWeatherMap(appid="56d28a5b8678ef42637810edae1d2b4e")

result = asyncio.run(
    client.clouds(x=1,y=1,z=1)
)
with open('map.png', 'wb') as png:
    png.write(result)
"""
client = api.OpenWeatherData(appid="56d28a5b8678ef42637810edae1d2b4e")

result = asyncio.run(
    client.one_call(lat=50.0, lon=50.0, units="imperial")
)
print(result)
"""
