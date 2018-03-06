import time
import os
import json
import paho.mqtt.client as mqtt
import Adafruit_DHT as dht
import RPi.GPIO as GPIO


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


def get_th_sensor(use_fahrenheit):
    """Get info from temperature/humidity sensor."""
    # Code to get humidity and temperature from the DHT22 sensor
    sensor = dht.DHT22
    pin = 4
    humidity, temp = dht.read_retry(sensor, pin)

    # temp = float(temp)

    # If the display should be in fahrenheit convert
    if use_fahrenheit:
        temp = celsius_to_fahrenheit(temp)

    # round to 1 digit
    temp = round(temp, 1)

    # humidity = float(humidity)

    # round to 1 digit
    humidity = round(humidity, 1)

    return humidity, temp


def check_states():
    """Read the states and return the set_temp, hvac_mode and fan_mode"""
    with open('States.json', 'r') as json_file:
        states = json.load(json_file)

    set_temp = float(states["set_temp"])
    hvac_mode = states["hvac_mode"]
    fan_mode = states["fan_mode"]

    return set_temp, hvac_mode, fan_mode


def show_pins(heat_running, cool_running, fan_on):
    """Show what the pins are doing"""
    print('Heat running: ' + str(heat_running))
    print('Cool running: ' + str(cool_running))
    print('Fan is on: ' + str(fan_on))


def print_thermostat(fan_mode, use_fahrenheit, set_temp,
                     temp_indoor, humidity_indoor):
    """Output the thermostat information to the screen"""
    print('Fan: ' + fan_mode + '\n')

    if use_fahrenheit:
        print('Current Temperature: ' + str(temp_indoor) + DEG + 'F')
    else:
        print('Current Temperature: ' + str(temp_indoor) + DEG + 'C')

    print('Current Humidity: ' + str(humidity_indoor) + '%\n')

    if use_fahrenheit:
        if set_temp is not '':
            print('Hold Temperature: ' + str(set_temp) + DEG + 'F\n')
        else:
            print('Hold Temperature: \n')
    else:
        print('Hold Temperature: ' + str(set_temp) + DEG + 'C\n')


def main():
    # Thermostat Setup
    # Read thermostat_config.json file
    with open('Configs/thermostat_config.json', 'r') as json_file:
        thermostat_config = json.load(json_file)

    set_temp = thermostat_config["default_set_temp"]
    hold_within = float(thermostat_config["hold_within"])
    use_fahrenheit = thermostat_config["use_fahrenheit"]

    # MQTT Setup
    # Read mqtt_config.json file
    with open('Configs/mqtt_config.json', 'r') as json_file:
        mqtt_config = json.load(json_file)

    # Assign MQTT Sever and Client ID
    mqtt_broker_address = mqtt_config["mqtt_broker_address"]
    mqtt_client_id = 'AHThermostat'

    # Assing MQTT Topics
    mqtt_current_temperature_topic = mqtt_config["current_temperature_topic"]
    mqtt_current_humidity_topic = mqtt_config["current_humidity_topic"]

    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker_address)

    fan_on = False

    heat_running = False
    cool_running = False

    # Set up GPIO using BCM numbering
    GPIO.setmode(GPIO.BCM)

    heat_pin = 17  # Pin 11 on Pi Zero W
    GPIO.setup(heat_pin, GPIO.OUT)
    cool_pin = 27  # Pin 13 on Pi Zero W
    GPIO.setup(cool_pin, GPIO.OUT)
    fan_pin = 22  # Pin 15 on Pi Zero W
    GPIO.setup(fan_pin, GPIO.OUT)

    # Create an infinite loop
    while True:
        set_temp, hvac_mode, fan_mode = check_states()

        # Get Indoor Sensor Info
        humidity_indoor, temp_indoor = get_th_sensor(use_fahrenheit)

        # Publish Indoor Temperature to MQTT server
        client.publish(mqtt_current_temperature_topic, temp_indoor)
        # Publish Indoor Humidity to MQTT server
        client.publish(mqtt_current_humidity_topic, temp_indoor)

        # HEATING Mode
        if hvac_mode == 'HEAT':
            # Make sure cooling is OFF
            cool_running = False
            GPIO.output(cool_pin, False)

            os.system('clear')
            print('Mode: HEAT')

            # If heat is not running and it is less than the
            # set_temp - hold_within Turn on Heat
            if not heat_running and temp_indoor < (set_temp - hold_within):
                heat_running = True
                GPIO.output(heat_pin, True)
                fan_on = True
                GPIO.output(fan_pin, True)

                print_thermostat(fan_mode, use_fahrenheit, set_temp,
                                 temp_indoor, humidity_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # If heat is running and it is less than the
            # set_temp + the hold_within Continue
            elif heat_running and temp_indoor < (set_temp + hold_within):
                print_thermostat(fan_mode, use_fahrenheit, set_temp,
                                 temp_indoor, humidity_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # Turn off Heat
            else:
                heat_running = False
                GPIO.output(heat_pin, False)

                if fan_mode == 'AUTO':
                    fan_on = False
                    GPIO.output(fan_pin, False)

                print_thermostat(fan_mode, use_fahrenheit, set_temp,
                                 temp_indoor, humidity_indoor)
                show_pins(heat_running, cool_running, fan_on)

        # COOLING Mode
        elif hvac_mode == 'COOL':
            # Make sure heating is OFF
            heat_running = False
            GPIO.output(heat_pin, False)

            os.system('clear')
            print('Mode: COOL')

            # If cool is not running and it is greater than the
            # set_temp + hold_within Turn on Cool
            if not cool_running and temp_indoor > (set_temp + hold_within):
                cool_running = True
                GPIO.output(cool_pin, True)
                fan_on = True
                GPIO.output(fan_pin, True)

                print_thermostat(fan_mode, use_fahrenheit, set_temp,
                                 temp_indoor, humidity_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # If cool is running and it is greater than the
            #  set_temp - the hold_within Continue
            elif cool_running and temp_indoor > (set_temp - hold_within):
                print_thermostat(fan_mode, use_fahrenheit, set_temp,
                                 temp_indoor, humidity_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # Turn off Cool
            else:
                cool_running = False
                GPIO.output(cool_pin, False)

                if fan_mode == 'AUTO':
                    fan_on = False
                    GPIO.output(fan_pin, False)

                print_thermostat(fan_mode, use_fahrenheit, set_temp,
                                 temp_indoor, humidity_indoor)
                show_pins(heat_running, cool_running, fan_on)

        # Mode OFF
        else:
            # Make sure heating and cooling are OFF
            heat_running = False
            GPIO.output(heat_pin, False)
            cool_running = False
            GPIO.output(cool_pin, False)

            os.system('clear')
            print('Mode: OFF')

            if fan_mode == 'ON':
                fan_on = True
                GPIO.output(fan_pin, True)
            elif fan_mode == 'AUTO':
                fan_on = False
                GPIO.output(fan_pin, False)

            print_thermostat(fan_mode, use_fahrenheit, set_temp,
                             temp_indoor, humidity_indoor)
            show_pins(heat_running, cool_running, fan_on)

        time.sleep(15)


if __name__ == '__main__':
    main()
