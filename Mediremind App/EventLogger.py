from EventSystem import EventType, event_system
from datetime import datetime
from config import EVENT_SENDING_TIME
from threading import Timer
from .Database.Models import Event

class EventLogger():
    def __init__(self):
        self.subscribe_to_events()
        self.events = []
        self.start_periodic_sending()

    def subscribe_to_events(self):
        for event in EventType:
            if 'REQUEST' in event.name or 'RESPONSE' in event.name:
                continue
            subscriber = self.create_subscriber(event)
            event_system.subscribe(event, subscriber)

    def create_subscriber(self, event_type):
        def subscriber_function(data):
            self.log_event(data, event_type)
        return subscriber_function

    def log_event(self, data, event_type: EventType):
        event = Event(type=event_type, data=data, time=datetime.now().time())
        self.events.append(event)   

    def send_events_to_database(self):
        event_system.publish(EventType.SEND_EVENTS, self.events)
        self.events = []
        self.start_periodic_sending()
        
    def start_periodic_sending(self):
        Timer(EVENT_SENDING_TIME * 60, self.send_events_to_database).start()
