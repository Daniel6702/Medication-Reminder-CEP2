import enum
from EventSystem import Event
from Database.DataBaseManager import DatabaseManager

class State(enum):
    IDLE = 1
    ACTIVE = 2
    MEDICATION_TAKEN = 3
    MEDICATION_MISSED = 4
    ALERT = 5 

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

class MedicationIntakeMonitor():
    pass

class ReminderController():
    def __init__(self, database_controller: DatabaseManager):
        self.state = State.IDLE
        self.database_controller = database_controller

    def update(self):
        if self.state == State.IDLE:
            self.idle()
        elif self.state == State.ACTIVE:
            self.active()
        elif self.state == State.MEDICATION_TAKEN:
            self.medication_taken()
        elif self.state == State.MEDICATION_MISSED:
            self.medication_missed()
        elif self.state == State.ALERT:
            self.alert()
    
    def idle(self):
        #check time and medication schedules. Change state to ACTIVE if medication is due
        pass

    def active(self):
        #Search for user. remind user at location
        #Check if medication is taken. Change state to MEDICATION_TAKEN if medication is taken
        #Check time and schedule. Change state to MEDICATION_MISSED if medication is missed
        pass

    def medication_taken(self):
        #change color to green
        #monitor medi intake. 
        #Change to Alert if medication taken again
        #Change to idle after 2 hours
        pass


    def medication_missed(self):
        #change color to red
        #monitor medi intake.
        #Change to MEDICATION_TAKEN if medication taken
        #Change to idle after 2 hours
        pass

    def alert(self):
        #flash red lights
        #play sound
        #send notification
        #if alert resolved change to idle.
        pass

    def handle_event(self, event):
        if event == Event.MEDICATION_TAKEN:
            self.state = State.MEDICATION_TAKEN
        elif event == Event.MEDICATION_MISSED:
            self.state = State.MEDICATION_MISSED
        elif event == Event.ALERT:
            self.state = State.ALERT
        elif event == Event.IDLE:
            self.state = State.IDLE
        elif event == Event.ACTIVE:
            self.state = State.ACTIVE