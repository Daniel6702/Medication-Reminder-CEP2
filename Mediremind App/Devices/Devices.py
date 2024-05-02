from abc import ABC, abstractmethod
from Database.Models import Device, DeviceEvent
from EventSystem import EventType, event_system
import time
import threading
from typing import Optional

class z2mInteractor(ABC):
    '''Defines a template for sending and receiving Zigbee messages via the event system.'''
    def send(self, topic, payload, zigbee_id):
        event_system.publish(EventType.SEND_ZIGBEE, (topic, payload, zigbee_id))

    @abstractmethod
    def receive(self, data):
        pass

class Actuator(Device, z2mInteractor):
    '''Represents actuator devices, capable of turning on and off.'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_state = "OFF"
        self._blinking = False
        self._blink_thread = None
        self._lock = threading.Lock()
        event_system.subscribe(EventType.TURN_ON, self.turn_on)
        event_system.subscribe(EventType.TURN_OFF, self.turn_off)
        event_system.subscribe(EventType.BLINK_TIMES, self.blink)
        event_system.subscribe(EventType.START_BLINK, self.start_blink)
        event_system.subscribe(EventType.STOP_BLINK, self.stop_blink)

    def event_is_not_for_this_device(self, data: DeviceEvent):
        return data.name and self.name != data.name or data.room and self.room != data.room
    
    def turn_on(self, data: DeviceEvent):
        if self.event_is_not_for_this_device(data): return
        self.send("set", {"state": "ON"}, self.zigbee_id)
        self.current_state = "ON"

    def turn_off(self, data: DeviceEvent):
        if self.event_is_not_for_this_device(data): return
        self.send("set", {"state": "OFF"}, self.zigbee_id)
        self.current_state = "OFF"

    def blink(self, data: DeviceEvent):
        if self.event_is_not_for_this_device(data): return
        if data.blink_interval and data.blink_times:
            self.start_blink(data)

    def _blink_thread_method(self, data: DeviceEvent):
        count = 0
        while self._blinking and (data.blink_times is None or count < data.blink_times):
            if not self._blinking: 
                break
            self.turn_on(data)
            time.sleep(data.blink_interval)
            self.turn_off(data)
            time.sleep(data.blink_interval)
            count += 1

    def start_blink(self, data: DeviceEvent):
        if self.event_is_not_for_this_device(data): return
        if data.blink_interval:
            with self._lock:
                if not self._blinking:
                    self._blinking = True
                    self._blink_thread = threading.Thread(target=self._blink_thread_method, args=(data,))
                    self._blink_thread.start()

    def stop_blink(self, data: DeviceEvent):
        if self.event_is_not_for_this_device(data): return
        with self._lock:
            if self._blinking:
                self._blinking = False
                if self._blink_thread.is_alive():
                    self._blink_thread.join()
                self._blink_thread = None

    
class Sensor(Device, z2mInteractor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class RGBStrip(Actuator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        event_system.subscribe(EventType.CHANGE_COLOR, self.set_color)
        self.current_color = None

    def set_color(self, data: DeviceEvent):
        if data.name and self.name != data.name or data.room and self.room != data.room: return
        if data.color:
            self.send("set", {"color": data.color}, self.zigbee_id)
            self.current_color = data.color

    def get_color(self):
        return self.current_color
    
    def receive(self, data):
        pass

class MotionSensor(Sensor):
    MIN_TIME_BETWEEN_EVENTS = 30  # seconds
    OCCUPANCY_RESET_INTERVAL = 120  # seconds

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_type = getattr(EventType, self.type.name, None)
        event_system.subscribe(self.event_type, self.receive)
        self.lock = threading.Lock()
        self.last_motion_time: Optional[float] = None
        self.occupancy = False
        self.occupancy_timer: Optional[threading.Timer] = None

    def reset_occupancy(self):
        with self.lock:
            self.occupancy = False
            event_system.publish(EventType.ROOM_EMPTY, self.room)
            print(f'RESET OCCUPANCY {self.name}')

    def receive(self, data: dict):
        topic: str = data.get('topic', '')
        parts = topic.split("zigbee2mqtt/")
        if len(parts) > 1 and parts[1] == self.name:
            with self.lock:
                current_time = time.time()
                if self.last_motion_time is None or (current_time - self.last_motion_time >= self.MIN_TIME_BETWEEN_EVENTS):
                    if data.get('event', {}).get('occupancy', False) and not self.occupancy:
                        self.occupancy = True
                        event_system.publish(EventType.MOTION_ALERT, self.room)
                        print(f'MOTION EVENT {self.name}')
                        self.cancel_and_reset_timer()
                        self.occupancy_timer = threading.Timer(self.OCCUPANCY_RESET_INTERVAL, self.reset_occupancy)
                        self.occupancy_timer.start()
                    self.last_motion_time = current_time

    def cancel_and_reset_timer(self):
        if self.occupancy_timer is not None:
            self.occupancy_timer.cancel()
            self.occupancy_timer = None

    def stop(self):
        """ Stop the sensor, canceling any active timers. """
        with self.lock:
            self.cancel_and_reset_timer()


class VibrationSensor(Sensor):
    def __init__(self, **kwargs):   
        super().__init__(**kwargs)
        event_type = getattr(EventType, self.type.name, None)
        event_system.subscribe(event_type, self.receive)
        self.lock = threading.Lock()
        self.last_medication_time = None
        self.min_time_between_medication_events = 30 #Seconds
        
    def receive(self, data: dict):
        print(data)
        print(f'VIBRATION: {self.name}')
        event = data.get('event', False)
        if event and event.get('action') == 'vibration' and event.get('vibration', False):
            with self.lock:
                current_time = time.time()
                if self.last_medication_time is None or (current_time - self.last_medication_time >= self.min_time_between_medication_events):
                    print("MEDICATION TAKEN")
                    event_system.publish(EventType.MEDICATION_TAKEN, self.room)
                    self.last_medication_time = current_time
                else:
                    print("MEDICATION EVENT BLOCKED: Less than 30 seconds since last event.")

class Switch(Actuator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def receive(self, data):
        pass

'''Motion sensor vibration received data: {'topic': 'zigbee2mqtt/vibration', 'type_': <Cep2Zigbee2mqttMessageType.DEVICE_EVENT: 'device_event'>, 'data': None, 'event': {'action': 'vibration', 'angle': 20, 'angle_x': 2, 'angle_x_absolute': 88, 'angle_y': -1, 'angle_y_absolute': 91, 'angle_z': -88, 'battery': 100, 'device_temperature': 30, 'linkquality': 51, 'power_outage_count': 6, 'strength': 38, 'vibration': True, 'voltage': 3055, 'x_axis': 24, 'y_axis': -18, 'z_axis': -734}, 'message': None, 'meta': None, 'status': None, 'state': None}'''
'''Motion sensor vibration received data: {'topic': 'zigbee2mqtt/vibration', 'type_': <Cep2Zigbee2mqttMessageType.DEVICE_EVENT: 'device_event'>, 'data': None, 'event': {'angle': 20, 'angle_x': 2, 'angle_x_absolute': 88, 'angle_y': -1, 'angle_y_absolute': 91, 'angle_z': -88, 'battery': 100, 'device_temperature': 30, 'linkquality': 84, 'power_outage_count': 6, 'strength': 38, 'vibration': True, 'voltage': 3055, 'x_axis': 24, 'y_axis': -18, 'z_axis': -734}, 'message': None, 'meta': None, 'status': None, 'state': None}'''

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