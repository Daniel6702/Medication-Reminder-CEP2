from time import sleep
from Zigbee.MQTTController import MQTTController
from EventSystem import EventSystem, Event
from Database.DataBaseManager import DatabaseManager
from config import base_api_url, api_token
from ReminderController import ReminderController
from Devices import DeviceController

'''
Dependencies:
    - Django server (API) must be running, and the connection configured (config.py)
    - The Mqtt broker must be running and configured (config.py)
    - USB antenna plugged in 
    - For simplicity, it should be run on the Pi
''' 

class MainSystem():
    def __init__(self):
        self.event_system = EventSystem()
        self.mqtt_controller = MQTTController(self.event_system)
        self.database_controller = DatabaseManager(base_api_url,api_token)
        self.device_controller = DeviceController(self.database_controller)
        self.reminder_system_controller = ReminderController(self.database_controller)

    def setup_connections(self):
        self.event_system.subscribe(Event.DEVICE_DISCOVERY, self.device_controller.get_devices)
    
    def start(self):
        self.setup_connections()
        self.mqtt_controller.start()
        self.loop()

    def loop(self):
        while True:
            #self.reminder_system_controller.update()
            sleep(1)

if __name__ == "__main__":
    reminder_system = MainSystem()
    reminder_system.start()