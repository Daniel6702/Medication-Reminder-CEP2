import enum

class Event(enum.Enum):
    ZigbeeMotionEvent = 1
    DEVICE_DISCOVERY = 2
    IDLE = 3
    ACTIVE = 4
    MEDICATION_TAKEN = 5
    MEDICATION_MISSED = 6
    ALERT = 7
    RGB_STRIP = 8
    PIR_SENSOR = 9
    SWITCH = 10
    VIBRATION_SENSOR = 11

class EventSystem:
    def __init__(self):
        self.subscribers = dict()

    def subscribe(self, event_type, fn):
        if not event_type in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(fn)

    def publish(self, event_type, data):
        if event_type in self.subscribers:
            for fn in self.subscribers[event_type]:
                fn(data)

