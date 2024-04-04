from .Distributer import ZigbeeMessageDistributer
from .Zigbee2mqttClient import Cep2Zigbee2mqttClient
from config import MQTT_BROKER_HOST, MQTT_BROKER_PORT

class MQTTController():
    def __init__(self, event_system):
        self.event_system = event_system
        self.distributer = ZigbeeMessageDistributer(self.event_system)
        self._z2m_client = Cep2Zigbee2mqttClient(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, on_message_clbk=self.distributer.analyze_message)

    def start(self) -> None:
        self._z2m_client.connect()
        print(f"Zigbee2Mqtt is {self._z2m_client.check_health()}")

    def stop(self) -> None:
        self._z2m_client.disconnect()