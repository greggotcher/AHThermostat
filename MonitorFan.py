import json
import paho.mqtt.client as mqtt
import time


Connected = False


def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")

        global Connected                # Use global variable
        Connected = True                # Signal connection

    else:

        print("Connection failed")


def on_message(client, userdata, message):
    message = message.payload.decode()

    with open('States.json', 'r') as json_file:
        states = json.load(json_file)

    states["fan_mode"] = message

    with open('States.json', 'w') as json_file:
        json.dump(states, json_file)

    print("Fan Mode Set: " + message)

    # Read mqtt_config.json file
    with open('Configs/mqtt_config.json') as json_file:
        mqtt_config = json.load(json_file)

    mqtt_fan_mode_state_topic = mqtt_config["fan_mode_state_topic"]

    client.publish(mqtt_fan_mode_state_topic, message)
    print("State Topic Set to " + message)


def main():
    # Read mqtt_config.json file
    with open('Configs/mqtt_config.json') as json_file:
        mqtt_config = json.load(json_file)

    # Assign MQTT Sever and Client ID
    mqtt_broker_address = mqtt_config["mqtt_broker_address"]
    mqtt_client_id = mqtt_config["mqtt_client_id"] + 'MonitorFan'

    # Assign MQTT Topics
    mqtt_fan_mode_command_topic = mqtt_config["fan_mode_command_topic"]

    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker_address)
    client.on_connect = on_connect

    client.on_message = on_message

    client.loop_start()

    client.subscribe(mqtt_fan_mode_command_topic)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("exiting")
        client.disconnect()
        client.loop_stop()


if __name__ == '__main__':
    main()
