from heucod import HeucodEvent as HeucodEvent_
from dataclasses import dataclass
from enum import Enum

@dataclass
class HeucodEvent(HeucodEvent_):
    pass

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
    id: int
    name: str
    connected_rooms: list

    def from_json(json_data):
        return Room(**json_data)

class DeviceType(Enum):
    ACTUATOR = "ACTUATOR"
    SENSOR = "SENSOR"
    RGB_STRIP = "RGB_STRIP"
    MOTION_SENSOR = "MOTION_SENSOR"
    VIBRATING_SENSOR = "VIBRATING_SENSOR"

@dataclass
class Device:
    id: int
    zigbee_id: str
    name: str
    room: Room
    type: DeviceType

    def from_json(json_data):
        return Device(**json_data)

class AlertType(Enum):
    LIGHT = "LIGHT"
    SOUND = "SOUND"

@dataclass
class AlertConfiguration:
    id: int
    alert_type: AlertType
    color_code: str
    sound_file: str
    room: Room

    def from_json(json_data):
        return AlertConfiguration(**json_data)