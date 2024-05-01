import enum

class EventType(enum.Enum):
    '''
    Represents different types of events that can be detected or generated within the system. 
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
    SEND_ZIGBEE = 12
    REQUEST_SCHEDULES = 13
    RESPONSE_SCHEDULES = 14
    ADD_DEVICE = 15
    HEUCOD_EVENT = 16
    REQUEST_DEVICES = 17
    RESPONSE_DEVICES = 18
    UPDATE_DB_INSTANCE = 19
    REQUEST_MQTT_CONF = 20
    RESPONSE_MQTT_CONF = 21
    REQUEST_ALERT_CONFS = 22
    RESPONSE_ALERT_CONFS = 23
    REQUEST_ROOMS = 24
    RESPONSE_ROOMS = 25
    UPDATE_DB_ATTRIBUTE = 26
    MOTION_ALERT = 27
    REMIND_HERE = 28
    REMIND_EVERYWHERE = 30
    NOTIFY_CAREGIVER = 31
    ALERT_RESOLVED = 32
    REQUEST_CAREGIVER = 33
    RESPONSE_CAREGIVER = 34
    NOTIFICATION = 35
    SEND_NOTIFICATION = 36
    REQUEST_STATE_CONFS = 37
    RESPONSE_STATE_CONFS = 38
    CHANGE_COLOR = 39
    SWITCH_LIGHT = 40
    PLAY_SOUND = 41
    SEND_EVENTS = 42
    TURN_ON = 43
    TURN_OFF = 44
    BLINK_TIMES = 45
    START_BLINK = 46
    STOP_BLINK = 47
    SETUP_FINISHED = 48

class EventSystem:
    '''
    Singleton EventSystem class.
    Maintains a subscription model where various functions (subscribers) can subscribe to specific event types.
    When an event of a subscribed type occurs, the EventSystem runs all subscribed functions with the published data.
    '''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSystem, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.subscribers = dict()
        self.__initialized = True

    def subscribe(self, event_type, fn):
        '''Allows a function 'fn' to subscribe to a specific event type 'event_type'.'''
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(fn)

    def publish(self, event_type, data):
        '''Publishes event data to all functions subscribed to the 'event_type'.'''
        if event_type in self.subscribers:
            for fn in self.subscribers[event_type]:
                fn(data)

event_system = EventSystem()


