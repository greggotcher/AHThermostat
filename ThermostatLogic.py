import time
import os
import json
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import RPi.GPIO as GPIO


# Constants
DEG = u'\N{DEGREE SIGN}'

# Globals
hvac_mode = "HEAT"
set_temp = 65.0
fan_mode = "AUTO"
temp_indoor = 65.0


def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")

        global Connected                # Use global variable
        Connected = True                # Signal connection

    else:

        print("Connection failed")


def celsius_to_fahrenheit(celsius):
    """Convert celsius to fahrenheit."""
    fahrenheit = 9.0/5.0 * celsius + 32

    return fahrenheit


def show_pins(heat_running, cool_running, fan_on):
    """Show what the pins are doing"""
    print('Heat running: ' + str(heat_running))
    print('Cool running: ' + str(cool_running))
    print('Fan is on: ' + str(fan_on))


def print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor):
    """Output the thermostat information to the screen"""
    print('Fan: ' + fan_mode + '\n')

    if use_fahrenheit:
        if set_temp is not '':
            print('Hold Temperature: ' + str(set_temp) + DEG + 'F\n')
        else:
            print('Hold Temperature: \n')
        if temp_indoor is not '':
            print('Current Temperature: ' + str(temp_indoor) + DEG + 'F\n')
        else:
            print('Current Temperature: \n')
    else:
        print('Hold Temperature: ' + str(set_temp) + DEG + 'C\n')
        print('Current Temperature: ' + str(temp_indoor) + DEG + 'C\n')


def mode_callback(client, userdata, message):
    global hvac_mode
    message = message.payload.decode()
    hvac_mode = message
    print(hvac_mode)


def temperature_callback(client, userdata, message):
    global set_temp
    message = message.payload.decode()
    set_temp = float(message)
    print(set_temp)


def fan_mode_callback(client, userdata, message):
    global fan_mode
    message = message.payload.decode()
    fan_mode = message
    print(fan_mode)


def current_temp_callback(client, userdata, message):
    global temp_indoor
    message = message.payload.decode()
    temp_indoor = message
    print(temp_indoor)


def main():
    global hvac_mode
    global set_temp
    global fan_mode
    global temp_indoor

    # Thermostat Setup
    # Read thermostat_config.json file
    with open('Configs/thermostat_config.json', 'r') as json_file:
        thermostat_config = json.load(json_file)

    # set_temp = thermostat_config["default_set_temp"]
    hold_within = float(thermostat_config["hold_within"])
    use_fahrenheit = thermostat_config["use_fahrenheit"]

    # MQTT Setup
    # Read mqtt_config.json file
    with open('Configs/mqtt_config.json', 'r') as json_file:
        mqtt_config = json.load(json_file)

    # Assign MQTT Sever and Client ID
    mqtt_broker_address = mqtt_config["mqtt_broker_address"]
    mqtt_client_id = mqtt_config["mqtt_client_id"] + 'ThermostatLogic'

    # Assign MQTT Topics
    mqtt_current_temperature_topic = mqtt_config["current_temperature_topic"]
    mqtt_mode_state_topic = mqtt_config["mode_state_topic"]
    mqtt_temperature_state_topic = mqtt_config["temperature_state_topic"]
    mqtt_fan_mode_state_topic = mqtt_config["fan_mode_state_topic"]

    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker_address)
    client.on_connect = on_connect

    client.subscribe(mqtt_mode_state_topic)
    client.subscribe(mqtt_temperature_state_topic)
    client.subscribe(mqtt_fan_mode_state_topic)

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
        client.message_callback_add(mqtt_mode_state_topic, mode_callback)
        client.message_callback_add(mqtt_temperature_state_topic,
                                    temperature_callback)
        client.message_callback_add(mqtt_fan_mode_state_topic,
                                    fan_mode_callback)
        client.message_callback_add(mqtt_current_temperature_topic,
                                    current_temp_callback)

        client.loop_start()

        ts = time.time()
        print(ts)

        print("Current Temperature: " + str(temp_indoor))

        # HEATING Mode
        if hvac_mode == 'HEAT':
            # Make sure cooling is OFF
            cool_running = False
            GPIO.output(cool_pin, False)

            os.system('clear')
            print('Mode: HEAT')

            # If heat is not running and it is less than the
            # set_temp - hold_within Turn on Heat
            if not heat_running and float(temp_indoor) < (float(set_temp) - hold_within):
                heat_running = True
                GPIO.output(heat_pin, True)
                fan_on = True
                GPIO.output(fan_pin, True)

                print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # If heat is running and it is less than the
            # set_temp + the hold_within Continue
            elif heat_running and float(temp_indoor) < (float(set_temp) + hold_within):
                print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # Turn off Heat
            else:
                heat_running = False
                GPIO.output(heat_pin, False)

                if fan_mode == 'AUTO':
                    fan_on = False
                    GPIO.output(fan_pin, False)

                print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
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
            if not cool_running and float(temp_indoor) > (float(set_temp) + hold_within):
                cool_running = True
                GPIO.output(cool_pin, True)
                fan_on = True
                GPIO.output(fan_pin, True)

                print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # If cool is running and it is greater than the
            #  set_temp - the hold_within Continue
            elif cool_running and float(temp_indoor) > (float(set_temp) - hold_within):
                print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
                show_pins(heat_running, cool_running, fan_on)
            # Turn off Cool
            else:
                cool_running = False
                GPIO.output(cool_pin, False)

                if fan_mode == 'AUTO':
                    fan_on = False
                    GPIO.output(fan_pin, False)

                print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
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

            print_thermostat(fan_mode, use_fahrenheit, set_temp, temp_indoor)
            show_pins(heat_running, cool_running, fan_on)

        time.sleep(10)


if __name__ == '__main__':
    main()
