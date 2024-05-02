from EventSystem import EventType, event_system
from Devices.Devices import Actuator, RGBStrip, Switch, MotionSensor, Sensor, VibrationSensor
import json
from Database.Models import DeviceType
from config import DEVICE_TYPES
from Database.Models import Device 

'''
We assume Zigbee2Mqtt and mqttbroker has been setup and is running. With the devices added.
'''

'''
BUG
We have more than one virtual device instance for each real world device. Results in double signaling
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
    def __init__(self):
        self.devices = []
        event_system.subscribe(EventType.RESPONSE_DEVICES,self.get_db_devices)
        event_system.subscribe(EventType.DEVICE_DISCOVERY, self.get_devices)

    def get_db_devices(self, devices: list): self.db_devices = devices
    
    def get_devices(self, message: list[dict]):
        self.devices = []
        '''
        Subscribed to the EVENT_DISCOVERY event, occurs on initialization of system. 
        Retrieves devices from z2m message and database.
        Compares with current list of devices and updates list and db if necessary.
        '''
        #Retrieve z2m devices
        z2m_devices = []
        for device in message:
            message_str = str(json.dumps(device))
            for device_type, rules in DEVICE_TYPES.items():
                if matches_rules(message_str, rules):
                    device_data = {
                        "device_id": None,
                        "zigbee_id": device.get('ieee_address', None),
                        "name": device.get('friendly_name', None),
                        "room": None,
                        "type": getattr(DeviceType, device_type)
                    }
                    z2m_device = self.create_device(device_data)
                    z2m_devices.append(z2m_device)
                    break
        
        event_system.publish(EventType.REQUEST_DEVICES,"new")  

        #if there is no devices in the datebase just add devices from z2m to db
        if not self.db_devices or self.db_devices == []:
            for z2m_device in z2m_devices:
                event_system.publish(EventType.ADD_DEVICE, z2m_device)
            self.devices = z2m_devices
            return 

        # Compare devices and update database if necessary
        for z2m_device in z2m_devices:
            found = False
            for db_device in self.db_devices:
                if z2m_device.zigbee_id == db_device.zigbee_id:
                    # Update z2m_device with details from db_device
                    z2m_device.device_id = db_device.device_id
                    z2m_device.room = db_device.room
                    found = True
                    break
            if not found:
                # Device is in z2m but not in DB, add it to the database
                event_system.publish(EventType.ADD_DEVICE, z2m_device)

        # Update self.devices with newly configured devices
        self.devices = [device for device in z2m_devices if device.room is not None]

        print("\nDEVICES: ")
        for device in self.devices: print(f'{device}')
        event_system.publish(EventType.SETUP_FINISHED, None)
        
    def create_device(self, device_data: Device):
        '''
        Creates specific device instances based on the provided device data.
        Determines the type of device and instantiates the corresponding device class.
        '''
        device_type = device_data['type']
        if device_type == DeviceType.RGB_STRIP:
            return RGBStrip(**device_data)
        elif device_type == DeviceType.PIR_SENSOR:
            return MotionSensor(**device_data)
        elif device_type == DeviceType.VIBRATION_SENSOR:
            return VibrationSensor(**device_data)
        elif device_type == DeviceType.SWITCH:
            return Switch(**device_data)
        else:
            raise ValueError(f"Unsupported device type: {device_type}")