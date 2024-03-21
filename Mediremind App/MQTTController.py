from Zigbee2mqttClient import (Cep2Zigbee2mqttClient,
                                   Cep2Zigbee2mqttMessage, Cep2Zigbee2mqttMessageType)

class Cep2Controller:
    HTTP_HOST = "http://localhost:8000"
    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883

    """ The controller is responsible for managing events received from zigbee2mqtt and handle them.
    By handle them it can be process, store and communicate with other parts of the system. In this
    case, the class listens for zigbee2mqtt events, processes them (turn on another Zigbee device)
    and send an event to a remote HTTP server.
    """

    def __init__(self, devices_model: Cep2Model) -> None:
        """ Class initializer. The actuator and monitor devices are loaded (filtered) only when the
        class is instantiated. If the database changes, this is not reflected.

        Args:
            devices_model (Cep2Model): the model that represents the data of this application
        """
        self._devices_model = devices_model
        self._z2m_client = Cep2Zigbee2mqttClient(host=self.MQTT_BROKER_HOST,
                                                  port=self.MQTT_BROKER_PORT,
                                                  on_message_clbk=self.__zigbee2mqtt_event_received)

    def start(self) -> None:
        """ Start listening for zigbee2mqtt events.
        """
        self._z2m_client.connect()
        print(f"Zigbee2Mqtt is {self._z2m_client.check_health()}")

    def stop(self) -> None:
        """ Stop listening for zigbee2mqtt events.
        """
        self._z2m_client.disconnect()

    def __update_devices(self, message: Cep2Zigbee2mqttMessage):
        """ Update devices based on message received.
        Args:
            message (Cep2Zigbee2mqttMessage): Message containing device information.
        """ 
        #Go through list of devices
        for device_info in message.data:
            #Retreive data from each device
            device_id = device_info.get('ieee_address', 'Not Found')
            device_type = 'Not Found'
            if 'definition' in device_info and device_info['definition'] is not None:
                if 'exposes' in device_info['definition']:
                    for expose in device_info['definition']['exposes']:
                        if 'type' in expose and expose['type'] != device_type:
                            device_type = expose['type']
                            break

            #Check if device already is in database
            existing_device = self._devices_model.find(device_id)
            
            #if not in database add it
            if not existing_device:
                self._devices_model.add(Cep2ZigbeeDevice(device_id, device_type))

    def __on_device_event(self, message: Cep2Zigbee2mqttMessage):
        tokens = message.topic.split("/")
        if len(tokens) <= 1:
            return

        # Retrieve the device ID from the topic.
        device_id = tokens[1]


    def __zigbee2mqtt_event_received(self, message: Cep2Zigbee2mqttMessage) -> None:
        """ Process an event received from zigbee2mqtt. This function given as callback to
        Cep2Zigbee2mqttClient, which is then called when a message from zigbee2mqtt is received.

        Args:
            message (Cep2Zigbee2mqttMessage): an object with the message received from zigbee2mqtt
        """
        # If message is None (it wasn't parsed), then don't do anything.
        if not message:
            return
        
        #Execute appropriate actions based on the type of message received

        if message.type_ == Cep2Zigbee2mqttMessageType.DEVICE_DISCOVERY:
            self.__update_devices(message)

        if message.type_ != Cep2Zigbee2mqttMessageType.DEVICE_EVENT:
            self.__on_device_event(message)

        print("")
        print(message)
        print("")