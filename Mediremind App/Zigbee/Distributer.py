from EventSystem import EventType, event_system
from .Zigbee2mqttClient import Cep2Zigbee2mqttMessage, Cep2Zigbee2mqttMessageType
from dataclasses import asdict
import json
from config import DEVICE_TYPES
from enum import Enum
from Devices.Device_Controller import matches_rules
import time


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.name  # Convert enum member to its name
        return json.JSONEncoder.default(self, o)

class ZigbeeMessageDistributer:
    '''Responsible for processing and routing messages from Zigbee devices through the MQTT broker to the appropriate components within the system.'''
    
    def __init__(self):
        # Timestamp of the last discovery event
        self.last_discovery_time = 0
        # Time period in seconds during which other events should be ignored after a discovery event
        self.ignore_period = 5  # You can adjust this value as needed

    def analyze_message(self, message: Cep2Zigbee2mqttMessage):
        '''Analyzes incoming messages from Zigbee2mqtt. Depending on the type of message, it publishes corresponding events to the event system. 
        Handles the identification of device types based on predefined rules'''
        if not message:
            return
        
        current_time = time.time()
        if message.type_ == Cep2Zigbee2mqttMessageType.DEVICE_DISCOVERY:
            self.last_discovery_time = current_time
            event_system.publish(EventType.DEVICE_DISCOVERY, message.data)

        elif message.type_ == Cep2Zigbee2mqttMessageType.DEVICE_EVENT:
            # Check if we are within the ignore period since the last discovery event
            if current_time - self.last_discovery_time < self.ignore_period:
                print("Ignoring device event due to recent discovery")
                return
            
            # Process the device event
            message_str = json.dumps(asdict(message), cls=EnhancedJSONEncoder)
            for device_type, rules in DEVICE_TYPES.items():
                if matches_rules(message_str, rules):
                    event_type = getattr(EventType, device_type)
                    event_system.publish(event_type, asdict(message))
                    return

            

