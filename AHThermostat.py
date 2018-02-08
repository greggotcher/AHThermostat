import time
import os
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
# import Adafruit_DHT


# Constants
DEG = u'\N{DEGREE SIGN}'


def celsius_to_fahrenheit(celsius):
    """Convert celsius to fahrenheit."""
    fahrenheit = 9.0/5.0 * celsius + 32

    return fahrenheit

def fahrenheit_to_celsius(fahrenheit):
    """Covert fahrenheit to celsius."""
    celsius = (fahrenheit - 32) * 5.0/9.0

    return celsius

def kelvin_to_celsius(kelvin):
    """Convert kelvin to celsius."""
    celsius = kelvin - 273.15

    return celsius

def kelvin_to_fahrenheit(kelvin):
    """Convert kelvin to fahrenheit."""
    celsius = kelvin_to_celsius(kelvin)
    fahrenheit = celsius_to_fahrenheit(celsius)

    return fahrenheit

def get_th_sensor(sensor_file, use_fahrenheit):
    """Get info from temperature/humidity sensor."""
    # Code to get humidity and temperature from the real sensor
    # humidity, temp = Adafruit_DHT.read_retry(11,4)

    # Dummy Code to read Fake Sensor for Temperature
    lines = open(sensor_file, 'r').readlines()
    temp = lines[0]
    humidity = lines[1]

    temp = float(temp)

    # If the display should be in fahrenheit convert
    if use_fahrenheit:
        temp = celsius_to_fahrenheit(temp)

    # round to 1 digit
    temp = round(temp, 1)

    humidity = float(humidity)

    # round to 1 digit
    humidity = round(humidity, 1)

    return humidity, temp

