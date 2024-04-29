from EventSystem import EventType, event_system
from time import sleep
import threading
from random import choice

class SimulationSystem():
    def __init__(self):
        event_system.subscribe(EventType.RESPONSE_ROOMS,self.get_rooms)
        event_system.publish(EventType.REQUEST_ROOMS, 'new')

    def get_rooms(self, rooms):
        self.rooms = rooms

    def Scenario1(self):
        while True:
            room = choice(self.rooms)
            event_system.publish(EventType.MOTION_ALERT, room)
            sleep(6)  

    def Scenario2(self):
        pass

    def run_scenario(self, scenario: function):
        thread = threading.Thread(target=scenario)
        thread.start()

    