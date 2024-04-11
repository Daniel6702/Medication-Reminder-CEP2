import json
from abc import ABC, abstractmethod
from Database.Models import Device 
from Database.Models import DeviceType
from Database.DataBaseManager import DatabaseManager
import uuid
from config import DEVICE_TYPES
from EventSystem import EventType, event_system
import time
import threading

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
    def __init__(self):
        self.devices = []
        self.actuators = []
        self.sensors = []
        event_system.subscribe(EventType.RESPONSE_DEVICES,self.get_db_devices)
        event_system.subscribe(EventType.DEVICE_DISCOVERY, self.get_devices)

    def get_db_devices(self, devices: list): self.db_devices = devices
    
    def get_devices(self, message: list[dict]):
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

        # Split devices into actuators and sensors
        self.actuators.clear()
        self.sensors.clear()

        for device in self.devices:
            if isinstance(device, Actuator):
                self.actuators.append(device)
            elif isinstance(device, Sensor):
                self.sensors.append(device)
        
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

    def remind(self, remind_configuration):
        '''
        Uses the systems actuators to remind the user. The method iterates
        through all actuators and activates those in the specified room with the 
        configuration provided (such as light color, audio, blinking, etc.)
        '''
        for actuator in self.actuators:
            if actuator.room == remind_configuration.room:
                actuator.turn_on()

                if hasattr(actuator, 'set_color') and remind_configuration.color_code:
                    actuator.set_color(remind_configuration.color_code)

                if hasattr(actuator, 'play_sound') and remind_configuration.sound_file:
                    actuator.play_sound(remind_configuration.sound_file)

                if hasattr(actuator, 'start_blink') and remind_configuration.blink:
                    # Check for continuous blinking or blink for a specified number of times
                    if remind_configuration.blink_times is not None:
                        actuator.blink_times(remind_configuration.blink_times, remind_configuration.blink_interval)
                    else:
                        actuator.start_blink(remind_configuration.blink_interval)
        
class z2mInteractor(ABC):
    '''Defines a template for sending and receiving Zigbee messages via the event system.'''
    def send(self, topic, payload, zigbee_id):
        event_system.publish(EventType.SEND_ZIGBEE, (topic, payload, zigbee_id))

    @abstractmethod
    def receive(self, data):
        pass

class Actuator(Device, z2mInteractor):
    '''Represents actuator devices, that are capable or turning on and off'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_state = "OFF"
        self._blinking = False
        self._blink_thread = None

    def turn_on(self):
        self.send("set", {"state": "ON"}, self.zigbee_id)
        self.current_state = "ON"

    def turn_off(self):
        self.send("set", {"state": "OFF"}, self.zigbee_id)
        self.current_state = "OFF"

    def get_state(self):
        return self.current_state
    
    def _blink_thread_method(self, interval, times=None):
        count = 0
        while self._blinking and (times is None or count < times):
            self.turn_on()
            time.sleep(interval)
            self.turn_off()
            time.sleep(interval)
            count += 1
        self._blinking = False

    def start_blink(self, interval=1):
        if not self._blinking:
            self._blinking = True
            self._blink_thread = threading.Thread(target=self._blink_thread_method, args=(interval,))
            self._blink_thread.start()

    def blink_times(self, times, interval=1):
        if not self._blinking:
            self._blinking = True
            self._blink_thread = threading.Thread(target=self._blink_thread_method, args=(interval, times))
            self._blink_thread.start()

    def stop_blink(self):
        self._blinking = False
        if self._blink_thread:
            self._blink_thread.join()
            self._blink_thread = None
    
class Sensor(Device, z2mInteractor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class RGBStrip(Actuator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_color = None

    def set_color(self, color):
        self.send("set", {"color": color}, self.zigbee_id)
        self.current_color = color

    def get_color(self):
        return self.current_color
    
    def receive(self, data):
        pass
    
class MotionSensor(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        event_type = getattr(EventType, self.type.name, None)
        event_system.subscribe(event_type, self.receive)
        
    def receive(self, data):
        print(f"Motion sensor {self.name} received data: {data}")

class VibrationSensor(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        event_type = getattr(EventType, self.type.name, None)
        event_system.subscribe(event_type, self.receive)
        
    def receive(self, data):
        print(f"Motion sensor {self.name} received data: {data}")

class Switch(Actuator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def receive(self, data):
        pass


'''
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

'''