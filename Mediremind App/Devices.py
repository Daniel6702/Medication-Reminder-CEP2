import json
from abc import ABC, abstractmethod
from Database.Models import Device as DeviceData
from Database.Models import DeviceType
from Database.DataBaseManager import DatabaseManager
import uuid
from config import DEVICE_TYPES

'''
We assume Zigbee2Mqtt and mqttbroker has been setup and is running. With the devices added.
'''

def matches_rules(message_str, rules):
    '''
    - If any keyword in 'must_not_have' is present in the message string, the function should return False.
    - All keywords in 'must_have' must be present in the message string for the condition to be true.
    - If 'or_must_have' is present, at least one of its keywords must be in the message string for the condition to be true.
    '''
    if 'must_not_have' in rules and any(keyword in message_str for keyword in rules['must_not_have']):
        return False

    if 'must_have' in rules and 'or_must_have' in rules:
        return all(keyword in message_str for keyword in rules['must_have']) or any(keyword in message_str for keyword in rules['or_must_have'])
    elif 'must_have' in rules and 'or_must_have' not in rules: 
        return all(keyword in message_str for keyword in rules['must_have'])
    elif 'must_have' not in rules and 'or_must_have' in rules: 
        return any(keyword in message_str for keyword in rules['or_must_have'])

class DeviceController():
    '''
    Contains and creates device instances. 
    Sensor devices analyze their respective z2m messages, containing relevant data,
    and use this information to draw conclusions, such as determining occupancy.
    Actuator devices can sent z2m message. To for instance turning on or off a light.
    '''
    def __init__(self, database_controller: DatabaseManager):
        self.database_controller = database_controller
        self.devices = []

    def get_devices(self, message: list[dict]):
        '''
        Subscribed to the EVENT_DISCOVERY event, occurs on initialization of system. 
        Retrieves devices from z2m message and database.
        Compares with current list of devices and updates list and db if necessay.  
        '''
        #Retrieve z2m devices
        z2m_devices = []
        for device in message:
            message_str = str(json.dumps(device))
            for device_type, rules in DEVICE_TYPES.items():
                if matches_rules(message_str, rules):
                    device = DeviceData(
                        device_id=None, 
                        zigbee_id=device.get('ieee_address', None),
                        name=device.get('friendly_name', None),
                        room=None,
                        type=getattr(DeviceType, device_type),
                    )
                    z2m_devices.append(device)
                    break
        
        #Retrieve database devices
        db_devices = self.database_controller.get_devices()

        print(db_devices)

        #if there is no devices in the datebase just add devices from z2m to db
        if not db_devices:
            for z2m_device in z2m_devices:
                self.database_controller.add_device(z2m_device)
            return 

        # Compare devices and update database if necessary
        for z2m_device in z2m_devices:
            found = False
            for db_device in db_devices:
                if z2m_device.zigbee_id == db_device.zigbee_id:
                    # Fill out the None fields from the db_device
                    z2m_device.device_id = db_device.device_id
                    z2m_device.room = db_device.room
                    found = True
                    break
            if not found:
                # Device is in z2m but not in DB, add it to the database
                self.database_controller.add_device(z2m_device)

        # Update self.devices with newly configured devices
        for z2m_device in z2m_devices:
            # Check if device is already in self.devices
            if not any(device.zigbee_id == z2m_device.zigbee_id for device in self.devices):
                self.devices.append(z2m_device)

        
class Device(ABC, DeviceData):
    def __init__(self, id, zigbee_id, name, room, type, client):
        super().__init__(id, zigbee_id, name, room, type)
        self.client = client

    @abstractmethod
    def receive(self, message):
        pass

    def send(self, topic, payload):
        topic = f"zigbee2mqtt/{self.zigbee_id}/{topic}"
        payload = json.dumps(payload)
        self.client.publish(topic, payload)


class Actuator(Device):
    def __init__(self, id, zigbee_id, name, room, type, client):
        super().__init__(id, zigbee_id, name, room, type, client)
        self.current_state = "OFF"

    def turn_on(self):
        self.send("set", {"state": "ON"})
        self.current_state = "ON"

    def turn_off(self):
        self.send("set", {"state": "OFF"})
        self.current_state = "OFF"
    
    def get_state(self):
        return self.current_state
    
class RGBStrip(Actuator):
    def __init__(self, id, zigbee_id, name, room, type, client):
        super().__init__(id, zigbee_id, name, room, type, client)
        self.current_color = None

    def set_color(self, color):
        #self.send("set", {"color": color})
        self.current_color = color

    def get_color(self):
        return self.current_color

class MotionSensor(Device):
    def __init__(self, id, zigbee_id, name, room, type, client):
        super().__init__(id, zigbee_id, name, room, type, client)
        self.value = 0

    def analyseMessage(self, message):
        pass

    def recieve(self, message):
        pass

class VibratingSensor(Device):
    def __init__(self, id, zigbee_id, name, room, type, client):
        super().__init__(id, zigbee_id, name, room, type, client)

    def recieve(self, message):
        pass

class DeviceDiscovery:
    def __init__(self):
        self.motion_sensor_keys = ['motion', 'pir', 'lumi', 'occupancy', 'Motion']
        self.rgb_strip_keys = ['RGB', 'rgb', 'RGB+CCT']
        self.vibration_sensor_key = ['vibration','Vibration']
        self.smart_plug_keys = ['switch', 'Switch', 'plug', 'Plug']
        self.__devices = []

    def process_message(self, message_data):
        for device in message_data:
            device_str = str(device)
            if any(word in device_str for word in self.motion_sensor_keys):
                self.__devices.append(Device(id=uuid.uuid4(),
                                    zigbee_id=device.get('ieee_address'),
                                    name=device.get('friendly_name'),
                                    type = DeviceType.MOTION_SENSOR))
            elif any(word in device_str for word in self.rgb_strip_keys):
                self.__devices.append(Device(id=uuid.uuid4(),
                                    zigbee_id=device.get('ieee_address'),
                                    name=device.get('friendly_name'),
                                    type = DeviceType.RGB_STRIP))
            elif any(word in device_str for word in self.vibration_sensor_key):
                self.__devices.append(Device(id=uuid.uuid4(),
                                    zigbee_id=device.get('ieee_address'),
                                    name=device.get('friendly_name'),
                                    type = DeviceType.VIBRATING_SENSOR))
            elif any(word in device_str for word in self.smart_plug_keys):
                self.__devices.append(Device(id=uuid.uuid4(),
                                    zigbee_id=device.get('ieee_address'),
                                    name=device.get('friendly_name'),
                                    type = DeviceType.ACTUATOR))

    def get_devices(self):
        return self.__devices