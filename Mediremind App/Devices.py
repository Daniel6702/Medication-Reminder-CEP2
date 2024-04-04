import json
from abc import ABC, abstractmethod
from Models import Device as DeviceData
from Models import DeviceType
import uuid

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