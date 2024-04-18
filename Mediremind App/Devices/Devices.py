from abc import ABC, abstractmethod
from Database.Models import Device 
from EventSystem import EventType, event_system
import time
import threading
        
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