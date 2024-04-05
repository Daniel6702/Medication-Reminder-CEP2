from EventSystem import EventSystem, Event
from .Zigbee2mqttClient import Cep2Zigbee2mqttMessage, Cep2Zigbee2mqttMessageType
from dataclasses import asdict
import json
from config import DEVICE_TYPES
from enum import Enum
from Devices import matches_rules

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.name  # Convert enum member to its name
        return json.JSONEncoder.default(self, o)

class ZigbeeMessageDistributer():
    '''Responsible for processing and routing messages from Zigbee devices through the MQTT broker to the appropriate components within the system.'''
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system

    def analyze_message(self, message: Cep2Zigbee2mqttMessage):
        '''Analyzes incoming messages from Zigbee2mqtt. Depending on the type of message, it publishes corresponding events to the event system. 
        Handles the identification of device types based on predefined rules'''
        if not message:
            return
        
        if message.type_ == Cep2Zigbee2mqttMessageType.DEVICE_DISCOVERY:
            self.event_system.publish(Event.DEVICE_DISCOVERY, message.data)

        elif message.type_ == Cep2Zigbee2mqttMessageType.DEVICE_EVENT:
            message_str = json.dumps(asdict(message), cls=EnhancedJSONEncoder)
            for device_type, rules in DEVICE_TYPES.items():
                if matches_rules(message_str, rules):
                    print(f"DEVICE_EVENT: {device_type}")
                    event_type = getattr(Event, device_type)
                    self.event_system.publish(event_type, message.data)
                    return
            print('Unknown Device')
            
