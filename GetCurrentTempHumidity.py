import time
import os
import json
import paho.mqtt.client as mqtt
import Adafruit_DHT as dht


# Constants
DEG = u'\N{DEGREE SIGN}'


def celsius_to_fahrenheit(celsius):
    """Convert celsius to fahrenheit."""
    fahrenheit = 9.0/5.0 * celsius + 32

    return fahrenheit


def get_th_sensor(use_fahrenheit):
    """Get info from temperature/humidity sensor."""
    # Code to get humidity and temperature from the DHT22 sensor
    sensor = dht.DHT22
    pin = 4
    humidity, temp = dht.read_retry(sensor, pin)

    # If the display should be in fahrenheit convert
    if use_fahrenheit:
        temp = celsius_to_fahrenheit(temp)

    # round to 1 digit
    temp = round(temp, 1)

    # round to 1 digit
    humidity = round(humidity, 1)

    return humidity, temp


def print_temp_humidity(use_fahrenheit, temp_indoor, humidity_indoor):
    """Output the thermostat information to the screen"""

    ts = time.time()
    print(ts)

    if use_fahrenheit:
        print('Current Temperature: ' + str(temp_indoor) + DEG + 'F')
    else:
        print('Current Temperature: ' + str(temp_indoor) + DEG + 'C')

    print('Current Humidity: ' + str(humidity_indoor) + '%\n')


def main():
    # Thermostat Setup
    # Read thermostat_config.json file
    with open('Configs/thermostat_config.json', 'r') as json_file:
        thermostat_config = json.load(json_file)

    use_fahrenheit = thermostat_config["use_fahrenheit"]

    # MQTT Setup
    # Read mqtt_config.json file
    with open('Configs/mqtt_config.json', 'r') as json_file:
        mqtt_config = json.load(json_file)

    # Assign MQTT Sever and Client ID
    mqtt_broker_address = mqtt_config["mqtt_broker_address"]
    mqtt_client_id = mqtt_config["mqtt_client_id"] + 'GetTempHumidity'

    # Assign MQTT Topics
    mqtt_current_temperature_topic = mqtt_config["current_temperature_topic"]
    mqtt_current_humidity_topic = mqtt_config["current_humidity_topic"]

    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker_address)

    # Set up GPIO using BCM numbering
    # GPIO.setmode(GPIO.BCM)

    # Create an infinite loop
    while True:
        # Get Indoor Sensor Info
        humidity_indoor, temp_indoor = get_th_sensor(use_fahrenheit)

        # Publish Indoor Temperature to MQTT server
        client.publish(mqtt_current_temperature_topic, temp_indoor)
        # Publish Indoor Humidity to MQTT server
        client.publish(mqtt_current_humidity_topic, humidity_indoor)

        os.system('clear')

        print_temp_humidity(use_fahrenheit, temp_indoor, humidity_indoor)

        time.sleep(30)


if __name__ == '__main__':
    main()
