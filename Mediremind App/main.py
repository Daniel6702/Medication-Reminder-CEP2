from time import sleep
from Zigbee.MQTTController import MQTTController
from EventSystem import EventSystem
from Database.DataBaseManager import DatabaseManager
from config import base_api_url, api_token
from ReminderController import ReminderController
   
class MainSystem():
    def __init__(self):
        self.event_system = EventSystem()
        self.mqtt_controller = MQTTController()
        self.database_controller = DatabaseManager(base_api_url,api_token)
        self.reminder_system_controller = ReminderController(self.database_controller)

    def setup_connections(self):
        pass
    
    def start(self):
        self.mqtt_controller.start()
        self.setup_connections()
        self.loop()

    def loop(self):
        while True:
            self.reminder_system_controller.update()
            sleep(1)

if __name__ == "__main__":
    reminder_system = MainSystem()
    reminder_system.start()