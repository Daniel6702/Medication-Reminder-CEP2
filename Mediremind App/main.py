from time import sleep
from Zigbee.MQTTController import MQTTController
from EventSystem import EventSystem
from DataBaseManager import DatabaseManager
from config import base_api_url, api_token
from ReminderController import ReminderController

class MainSystem():
    def __init__(self):
        self.event_system = EventSystem()
        self.mqtt_controller = MQTTController()
        self.database_controller = DatabaseManager(base_api_url,api_token)
        self.reminder_system_controller = ReminderController()

    def setup_connections(self):
        pass
    
    def start(self):
        self.mqtt_controller.start()

    def loop(self):
        while True:
            sleep(1)

if __name__ == "__main__":
    reminder_system = MainSystem()
    reminder_system.start()



'''        schedules = self.database_manager.get_medication_schedules()
        devices = self.database_manager.get_devices()
        mqtt_configuration = self.database_manager.get_mqtt_configuration()
        alert_configuration = self.database_manager.get_alert_configuration()
        rooms = self.database_manager.get_rooms()

        self.reminder_controller = ReminderController.ReminderController(schedules, devices, alert_configuration, rooms)'''