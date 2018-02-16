def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
 
        print("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
 
        print("Connection failed")
 
def on_message(client, userdata, message):
    print ("Message received: "  + message.payload.decode())


def main():

    import json
    import paho.mqtt.client as mqtt
    import time
    import paho.mqtt.subscribe as subscribe
    

    # Read mqtt.config file
    with open('Configs\mqtt.config') as json_file:  
        mqtt_config = json.load(json_file)

    # Assign MQTT Sever and Client ID
    mqtt_broker_address = mqtt_config["mqtt_broker_address"]
    mqtt_client_id = mqtt_config["mqtt_client_id"]
    
    # Assing MQTT Topics
    mqtt_temperature_state_topic = mqtt_config["temperature_state_topic"]
        
    client = mqtt.Client(mqtt_client_id)
    client.connect(mqtt_broker_address)
    
    while True:

        client.on_message= on_message

        # heat_cool_mode = check_heat_cool_mode()  <--REMOVED TO TEST MQTT
        client.loop_start()

        client.subscribe(mqtt_temperature_state_topic)

        try:
            while True:
                time.sleep(1)
 
        except KeyboardInterrupt:
            print ("exiting")
            client.disconnect()
            client.loop_stop()
            break


if __name__ == '__main__':
    main()