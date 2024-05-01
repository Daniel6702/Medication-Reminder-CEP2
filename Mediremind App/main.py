from time import sleep
from Zigbee.MQTTController import MQTTController
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from config import base_api_url, api_token
from ReminderController import ReminderSystem
from Devices.Device_Controller import DeviceController
from NotificationController import NotificationController
import threading
from time import sleep
'''
Dependencies:
    - Django server (API) must be running (settings.py), and the connection configured (config.py)
    - The Mqtt broker must be running and configured (config.py)
    - USB antenna plugged in 
    - For simplicity, it should be run on the Pi
''' 

'''
TODO
update models
update db manager
implement stateconfig in rc 
'''

class MainSystem():
    '''Central class of the system that integrates the various components and controllers, and allows them to work together.'''
    def __init__(self):
        self.setup_finished = threading.Event()
        self.running = False
        event_system.subscribe(EventType.SETUP_FINISHED, self.start)
        self.database_controller = DatabaseManager(base_api_url, api_token)
        self.device_controller = DeviceController()
        self.mqtt_controller = MQTTController()
        self.mqtt_controller.start()
        self.notification_controller = NotificationController()

    def start(self, a):
        if self.running is False:
            print("Setup finished. Starting the system...")
            self.reminder_system_controller = ReminderSystem()
            self.running = True
            self.setup_finished.set()
            self.thread = threading.Thread(target=self.loop)
            self.thread.start()

    def loop(self):
        '''Main loop of the system, continuously updating the reminder system.'''
        while self.running:
            self.reminder_system_controller.update()
            sleep(1)

    def stop(self):
        '''Stop the system by terminating the loop and joining the thread.'''
        self.running = False
        self.thread.join()


if __name__ == "__main__":
    reminder_system = MainSystem()
    reminder_system.setup_finished.wait()
    try:
        while True:  # Main thread remains responsive
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down the system...")
        reminder_system.stop()

