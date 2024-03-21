import Devices

class UserPresenceController():
    def __init__(self, motion_sensors):
        pass

    def update(self):
        pass

class AlertController():
    def __init__(self, alert_configuration, actuator_devices):
        pass

    def update(self):
        pass

class ReminderController():
    def __init__(self, schedules, devices, alert_configuration, rooms):
        motion_sensors = [device for device in devices if isinstance(device, Devices.MotionSensor)]
        UserPresenceController(motion_sensors)

        actuator_devices = [device for device in devices if isinstance(device, Devices.Actuator)]
        AlertController(alert_configuration, actuator_devices)

    def update(self):
        pass