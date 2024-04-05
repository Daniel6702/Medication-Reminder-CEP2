import enum

class Event(enum.Enum):
    '''
    Event is an enumeration representing different types of events that can be detected or generated within the system. 
    Acts like topics / channels functions can subscribe to. 
    '''
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
    '''
    Maintains a subscription model where various functions (subscribers) can subscribe to specific event types. 
    When an event of a subscribed type occurs, the EventSystem runs all subscribed functions with the published data.
    '''
    def __init__(self):
        self.subscribers = dict()

    def subscribe(self, event_type, fn):
        '''Allows a function 'fn' to subscribe to a specific event type 'event_type'.'''
        if not event_type in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(fn)

    def publish(self, event_type, data):
        '''Publishes event data to all functions subscribed to the 'event_type'.'''
        if event_type in self.subscribers:
            for fn in self.subscribers[event_type]:
                fn(data)
