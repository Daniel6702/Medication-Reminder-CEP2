from enum import Enum
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from abc import ABC, abstractmethod
import datetime
from Devices import DeviceController

class State(ABC):
    def __init__(self, reminder_system):
        self.reminder_system = reminder_system

    @abstractmethod
    def handle(self):
        pass

class IdleState(State):
    def handle(self):
        # Idle state logic, waiting for the next medication time.
        print("System is idle.")

class ActiveState(State):
    def handle(self):
        # Active state logic, checking if medication is taken.
        if self.reminder_system.is_medication_time():
            self.reminder_system.change_state(MedicationMissedState(self.reminder_system))
        else:
            self.reminder_system.change_state(IdleState(self.reminder_system))

class MedicationTakenState(State):
    def handle(self):
        # Medication taken logic.
        print("Medication has been taken.")
        # Switch to idle after medication is taken.
        self.reminder_system.change_state(IdleState(self.reminder_system))

class MedicationMissedState(State):
    def handle(self):
        # Medication missed logic.
        print("Medication missed, alerting.")
        self.reminder_system.change_state(AlertState(self.reminder_system))

class AlertState(State):
    def handle(self):
        # Alerting logic.
        print("Alerting the user.")
        self.reminder_system.send_alert()
        self.reminder_system.change_state(IdleState(self.reminder_system))

class ReminderSystem:
    def __init__(self, device_controller: DeviceController):
        self.setup_connections()
        self.state = IdleState(self)
        self.device_controller = device_controller
        event_system.publish(EventType.REQUEST_ROOMS,'new')
        event_system.publish(EventType.REQUEST_ALERT_CONFS,'new')

    def setup_connections(self):
        event_system.subscribe(EventType.RESPONSE_ROOMS,self.get_rooms)
        event_system.subscribe(EventType.RESPONSE_ALERT_CONFS,self.get_alert_configurations)

    def get_rooms(self, rooms):
        print(rooms)

    def get_alert_configurations(self, alert_configurations):
        print(f"Alert confs: {alert_configurations}")

    def change_state(self, state):
        self.state = state
        self.state.handle()

    def update(self):
        self.state.handle()

    def is_medication_time(self):
        return False





'''
class ReminderController():
    def __init__(self, database_controller: DatabaseManager):
        self.state = State.IDLE
        self.database_controller = database_controller
        self.device_controller = None
    
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

'''