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

    states["hvac_mode"] = message

    with open('States.json', 'w') as json_file:
        json.dump(states, json_file)

    print("Heat Cool Mode: " + message)


def main():
    # Read mqtt_config.json file
    with open('Configs\mqtt_config.json') as json_file:
        mqtt_config = json.load(json_file)

    # Assign MQTT Sever and Client ID
    mqtt_broker_address = mqtt_config["mqtt_broker_address"]
    mqtt_client_id = 'GetModeState'

    # Assing MQTT Topics
    mqtt_mode_state_topic = mqtt_config["mode_state_topic"]

    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker_address)
    client.on_connect = on_connect

    client.on_message = on_message

    client.loop_start()

    client.subscribe(mqtt_mode_state_topic)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("exiting")
        client.disconnect()
        client.loop_stop()


if __name__ == '__main__':
    main()
