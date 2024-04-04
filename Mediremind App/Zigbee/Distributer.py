from EventSystem import EventSystem, EventType
from Zigbee2mqttClient import Cep2Zigbee2mqttMessage, Cep2Zigbee2mqttMessageType

class ZigbeeMessageDistributer():
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system

    def analyze_message(self, message: Cep2Zigbee2mqttMessage):
        if message.type_ == Cep2Zigbee2mqttMessageType.DEVICE_DISCOVERY:
            self.event_system.publish(EventType.DEVICE_DISCOVERY)
            
