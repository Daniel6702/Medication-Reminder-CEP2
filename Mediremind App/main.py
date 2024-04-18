from time import sleep
from Zigbee.MQTTController import MQTTController
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from config import base_api_url, api_token
from ReminderController import ReminderSystem
from Devices.Device_Controller import DeviceController
from NotificationController import NotificationController

'''
Dependencies:
    - Django server (API) must be running (settings.py), and the connection configured (config.py)
    - The Mqtt broker must be running and configured (config.py)
    - USB antenna plugged in 
    - For simplicity, it should be run on the Pi
''' 

class MainSystem():
    '''Central class of the system that integrates the varioues components and controllers, and allows them to work together.'''
    def __init__(self):
        self.mqtt_controller = MQTTController()
        self.database_controller = DatabaseManager(base_api_url,api_token)
        self.device_controller = DeviceController()
        self.reminder_system_controller = ReminderSystem()
        self.notification_controller = NotificationController()
    
    def start(self):
        '''Starts the main workflow of the system. It sets up connections, starts the MQTT controller, and enters the main loop.'''
        self.mqtt_controller.start()
        self.loop()

    def loop(self):
        '''Main loop of the system, continuously updating the reminder system'''
        while True:
            self.reminder_system_controller.update()
            sleep(1)

if __name__ == "__main__":
    reminder_system = MainSystem()
    reminder_system.start()


