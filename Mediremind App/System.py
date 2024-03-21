import Devices
import MQTTController
from Database import DataBaseManager
import ReminderController

class System():
    def __init__(self):
        self.database_manager = DataBaseManager()

    def start(self):
        schedules = self.database_manager.get_medication_schedules()
        devices = self.create_devices(self.database_manager.get_devices())
        mqtt_configuration = self.database_manager.get_mqtt_configuration()
        alert_configuration = self.database_manager.get_alert_configuration()
        rooms = self.database_manager.get_rooms()

        self.reminder_controller = ReminderController.ReminderController(schedules, devices, alert_configuration, rooms)

        self.mqtt_controller = MQTTController.Cep2Controller(devices, mqtt_configuration)
        self.mqtt_controller.start()

        self.loop()

    def loop(self):
        while True:
            self.reminder_controller.update()




