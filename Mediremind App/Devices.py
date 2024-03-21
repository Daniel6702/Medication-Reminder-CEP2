import json
from abc import ABC, abstractmethod
from ..Database.Models import Device as DeviceData

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

