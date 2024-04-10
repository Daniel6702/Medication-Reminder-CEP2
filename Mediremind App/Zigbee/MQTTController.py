from .Distributer import ZigbeeMessageDistributer
from .Zigbee2mqttClient import Cep2Zigbee2mqttClient
from config import MQTT_BROKER_HOST, MQTT_BROKER_PORT

class MQTTController():
    '''
    Responsible for managing the MQTT communication within the system. 
    Acts as a bridge between MQTT messages and the event system. 
    By distributing the messages to their corresponding handlers.
    '''
    def __init__(self):
        self.distributer = ZigbeeMessageDistributer()
        self._z2m_client = Cep2Zigbee2mqttClient(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, on_message_clbk=self.distributer.analyze_message)

    def start(self) -> None:
        self._z2m_client.connect()
        print(f"Zigbee2Mqtt is {self._z2m_client.check_health()}")

    def stop(self) -> None:
        self._z2m_client.disconnect()