
import requests
from datetime import datetime
from termcolor import colored, cprint

from credentials import api_key
from asciiart import *
from constants import PADDING, HIGH_WIND_SPEEDS


def current_location():
	'''Gets user's current location from ipinfio.io.'''

	loc_api = "https://ipinfo.io/loc"
	loc_req = requests.get(loc_api).text
	lat, lon = (float(ll) for ll in loc_req.split(','))
	return lat, lon


def call_weather_api():
	'''Returns json from calling openweathermap.org.
	This uses the user's latitude and longitude, from ipinfo.io.'''

	lat, lon = current_location()
	weather_api = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&units=imperial&lon={lon}&appid={api_key}"
	weather_request = requests.get(weather_api).json()
	return weather_request


def parse_json():
	'''Parses some of the available data, from the api call.
	https://openweathermap.org/current#data'''

	data = call_weather_api()

	name = data['name']
	condition_id = data['weather'][0]['id']
	condition = data['weather'][0]['main']
	wind_speed = data['wind']['speed']
	temperature = data['main']['temp']
	feels_like = data['main']['feels_like']

	return name, condition_id, condition, temperature, feels_like, wind_speed


def is_nighttime():
	hour = datetime.now().hour
	# naive approach - day-time defined as 6:00 AM -> 8:00 PM
	nighttime = not (6 <= hour <= 20)
	return nighttime


def select_ascii(condition_id, wind_speed):
	'''Selects ASCII art for the given conditions, using the ID from API. 
	condition_id is a three-digit number provided with the weather API.
	The first digit is the main-category, with the second and third digit
	being subcategories of weather.
	https://openweathermap.org/weather-conditions'''
	
	category, subcategory = condition_id // 100, condition_id % 100
	windy = wind_speed >= HIGH_WIND_SPEEDS 
	nighttime = is_nighttime()

	match category, subcategory, windy, nighttime:
		case (2|5),_,True: ascii_art = chaos; color = 'grey'	
		case 8,0,_,True: ascii_art = night; color = 'magenta'
		case 6,_,_,True: ascii_art = snow; color = 'blue'
		case _,_,True,_: ascii_art = wind; color = 'blue'
		case 8,0,_,_: ascii_art = sunny; color = 'yellow'
		case 2,_,_,_: ascii_art = thunderstorm; color = 'yellow'		
		case 3,_,_,_: ascii_art = drizzle; color = 'cyan'
		case 5,_,_,_: ascii_art = rain; color = 'blue'
		case 6,_,_,_: ascii_art = snow; color = 'white'
		case 8,(2|3),_,_: ascii_art = partial_clouds; color = 'blue'
		case 8,4,_,_: ascii_art = clouds; color = 'blue'
		case 7,_,_,_: ascii_art = fog; color = 'grey'
		case _,_,_,_: ascii_art = "?"; color = 'white'

	return ascii_art, color


def format_weather():
	'''Formats weather information for printing to the terminal.
	The ascii art is selected from asciiart.py, using the select_ascii() function.'''

	name, condition_id, condition, temperature, feels_like, wind_speed = parse_json()	
	ascii_art, color = select_ascii(condition_id, wind_speed)
	time = datetime.today().strftime("%I:%M %p") 
	temperature, feels_like, wind_speed = f'{round(temperature)}°F', f'{round(feels_like)}°F', f'{round(wind_speed)} mph'

	weather_text = [
		'{:<13} feels like {}'.format(temperature, feels_like),
		'{:<13} wind {}'.format(condition, wind_speed),
		'{:<13} thanks to OpenWeatherMap.org'.format(time)
	]
	
	return weather_text, ascii_art, color


def print_weather():
	'''Outputs weather information to the terminal, using termcolor library.'''

	weather_text, ascii_art, color = format_weather()
	for row in zip(ascii_art, weather_text):
		combined = PADDING.join(row)
		cprint(combined, color)
	

def main():
	print_weather()


if __name__ == '__main__':
	main()
