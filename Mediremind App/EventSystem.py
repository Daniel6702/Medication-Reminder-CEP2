import enum

class EventType(enum.Enum):
    ZigbeeMotionEvent = 1
    DEVICE_DISCOVERY = 2

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

