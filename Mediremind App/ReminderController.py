from enum import Enum
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from abc import ABC, abstractmethod
import datetime

'''
This Python module defines the core logic of the remind mechanisms. The system is structured around a state machine pattern,
allowing it to transition between various states based on medication schedules, user interactions, and system events.
'''

class ReminderSystem:
    '''Initializes the system state, handles state changes. Retrieves data from the db through events'''
    def __init__(self):
        self.setup_connections()
        self.state = IdleState(self)
        event_system.publish(EventType.REQUEST_ROOMS,'new')
        event_system.publish(EventType.REQUEST_ALERT_CONFS,'new')
        event_system.publish(EventType.REQUEST_SCHEDULES,'new')

    def setup_connections(self):
        event_system.subscribe(EventType.RESPONSE_ROOMS,self.get_rooms)
        event_system.subscribe(EventType.RESPONSE_ALERT_CONFS,self.get_alert_configurations)
        event_system.subscribe(EventType.RESPONSE_SCHEDULES, self.get_medication_schedules)

    def get_rooms(self, rooms):
        self.rooms = rooms
        print(f"ROOMS: {rooms}")

    def get_alert_configurations(self, alert_configurations):
        self.alert_configurations = alert_configurations
        print(f"ALERT CONFS: {alert_configurations}")

    def get_medication_schedules(self,schedules):
        self.schedules = schedules
        print(f"SCHEDULES: {schedules}")

    def change_state(self, state):
        self.state = state
        self.state.handle()

    def update(self):
        self.state.handle()

    def is_time_passed(time: datetime.datetime):
        now = datetime.datetime.now()
        return now.time() >= time.time()

class State(ABC):
    '''It provides a common interface for all states to implement the handle
    method and allows optional setup procedures for each state.'''
    def __init__(self, reminder_system: ReminderSystem):
        self.reminder_system = reminder_system
        self.setup()

    @abstractmethod
    def handle(self):
        pass

    def setup(self):
        pass

class IdleState(State):
    '''Represents the idle state of the reminder system. It checks for medication times
    and changes to ActiveState if it's time for medication.'''
    def is_medication_time(self):
        for schedule in self.reminder_system.schedules:
            schedule_time = datetime.datetime.strptime(schedule.reminder_time, "%H:%M:%S").time()
            if self.reminder_system.is_time_passed(schedule_time):
                return True
        return False

    def handle(self):
        print("IDLE")
        if self.is_medication_time():
            self.reminder_system.change_state(ActiveState(self.reminder_system))

class ActiveState(State):
    def setup(self):
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)

    def get_motion_alert(self, room):
        alert_configuration = None #Temp
        event_system.publish(EventType.REMIND_HERE, alert_configuration)

    def medication_event(self, data):
        #TODO: use data from vibration sensor to ensure medication has been taken
        self.reminder_system.change_state(MedicationTakenState(self.reminder_system))

    def is_medication_time_missed(self):
        for schedule in self.reminder_system.schedules:            
            window_end_time = datetime.datetime.strptime(schedule.reminder_time, "%H:%M:%S") + datetime.timedelta(hours=schedule.time_window)
            if self.reminder_system.is_time_passed(window_end_time):
                return True
        return False

    def handle(self):
        print("IT WORKED")
        if self.is_medication_time_missed():
            self.reminder_system.change_state(MedicationMissedState(self.reminder_system))

class MedicationTakenState(State):
    def setup(self):
        self.last_reminder_date = datetime.date.today()  
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)

    def medication_event(self, data):
        self.reminder_system.change_state(AlertState(self.reminder_system))

    def get_motion_alert(self, room):
        alert_configuration = None #Temp. Apply room to conf
        event_system.publish(EventType.REMIND_HERE, alert_configuration)

    def is_next_day(self):
        current_date = datetime.date.today()
        return current_date > self.last_reminder_date

    def handle(self):
        if self.is_next_day():
            self.reminder_system.change_state(IdleState(self.reminder_system))

class MedicationMissedState(State):
    def setup(self):
        self.last_reminder_date = datetime.date.today()  
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)

    def medication_event(self, data):
        self.reminder_system.change_state(MedicationTakenState(self.reminder_system))

    def get_motion_alert(self, room):
        alert_configuration = None #Temp. Apply room to conf
        event_system.publish(EventType.REMIND_HERE, alert_configuration)

    def is_next_day(self):
        current_date = datetime.date.today()
        return current_date > self.last_reminder_date

    def handle(self):
        if self.is_next_day():
            self.reminder_system.change_state(IdleState(self.reminder_system))

class AlertState(State):
    def setup(self):
        alert_configuration = None
        event_system.publish(EventType.REMIND_EVERYWHERE,alert_configuration)
        event_system.publish(EventType.NOTIFY_CAREGIVER,"Medication Taken again")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.ALERT_RESOLVED,self.alert_resolved)
        self.number_of_meds_taken = 2
    
    def alert_resolved(self,data):
        self.reminder_system.change_state(IdleState(self.reminder_system))

    def medication_event(self, data):
        #TODO: use data from vibration sensor to ensure medication has been taken
        self.number_of_meds_taken += 1
        if self.number_of_meds_taken > 10:
            event_system.publish(EventType.NOTIFY_CAREGIVER,f"FUCK FUCK FUCK {self.number_of_meds_taken}")
            return
        elif self.number_of_meds_taken > 50:
            event_system.publish(EventType.NOTIFY_CAREGIVER,f"HE DEAD {self.number_of_meds_taken}")
            return
        event_system.publish(EventType.NOTIFY_CAREGIVER,f"WE HAVE A PROBLEM {self.number_of_meds_taken}")

    def get_motion_alert(self, room):
        alert_configuration = None #Temp. Apply room to conf
        event_system.publish(EventType.REMIND_HERE, alert_configuration)

    def handle(self):
        pass