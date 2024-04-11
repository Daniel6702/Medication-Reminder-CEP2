from .heucod import HeucodEvent as HeucodEvent_
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from uuid import uuid4

'''
Defines the core data structures of system. 
- users
- medication schedules
- MQTT settings
- rooms
- devices
- alert confs
'''

@dataclass
class HeucodEvent(HeucodEvent_):
    pass

@dataclass
class User:
    username: str = None
    email: str = None

@dataclass
class MedicationSchedule:
    user: str
    schedule_id: int
    medication_name: str
    reminder_time: str
    time_window: str
    dosage: str
    instructions: str

    def from_json(json_data):
        return MedicationSchedule(**json_data)

@dataclass
class MQTTConfiguration:
    user: str
    id: int
    broker_address: str
    port: int
    username: str
    password: str

    def from_json(json_data):
        return MQTTConfiguration(**json_data)

@dataclass
class Room:
    room_id: str
    user: str
    name: str
    connected_rooms: list

    def from_json(json_data):
        return Room(**json_data)

class DeviceType(Enum):
    RGB_STRIP = "RGB_STRIP"
    PIR_SENSOR = "PIR_SENSOR"
    SWITCH = "SWITCH"
    VIBRATION_SENSOR = "VIBRATION_SENSOR"

@dataclass
class Device:
    device_id: str
    zigbee_id: str
    name: str
    type: DeviceType
    user: User = None
    status: str = None
    room: Optional[Room] = None  # room is optional now

    def from_json(json_data):
        return Device(**json_data)

class AlertType(Enum):
    LIGHT = "LIGHT"
    SOUND = "SOUND"

@dataclass
class AlertConfiguration:
    alert_id: str
    user: str
    alert_type: AlertType
    color_code: str
    sound_file: str
    room: Room
    blink: bool = False
    blink_interval: float = 1.0  # seconds
    blink_times: int = None

    def from_json(json_data):
        return AlertConfiguration(**json_data)