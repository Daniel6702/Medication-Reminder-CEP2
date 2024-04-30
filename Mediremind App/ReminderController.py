from enum import Enum
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from Database.Models import StateConfig, DeviceEvent
from time import sleep
'''
This Python module defines the core logic of the remind mechanisms. The system is structured around a state machine pattern,
allowing it to transition between various states based on medication schedules, user interactions, and system events.
'''

def hex_to_rgb(hex_color: str) -> dict:
    hex_color = hex_color.lstrip('#')
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return {"r": r, "g": g, "b": b}

class ReminderSystem:
    '''Initializes the system state, handles state changes. Retrieves data from the db through events'''
    def __init__(self):
        self.setup_connections()
        self.initialize_data()
        self.state = IdleState(self)

    def initialize_data(self):
        '''Publish events to request initial data load.'''
        event_system.publish(EventType.REQUEST_ROOMS, 'new')
        event_system.publish(EventType.REQUEST_STATE_CONFS, 'new')
        event_system.publish(EventType.REQUEST_SCHEDULES, 'new')

    def setup_connections(self):
        event_system.subscribe(EventType.RESPONSE_ROOMS,self.get_rooms)
        event_system.subscribe(EventType.RESPONSE_STATE_CONFS,self.get_state_configurations)
        event_system.subscribe(EventType.RESPONSE_SCHEDULES, self.get_medication_schedules)

    def get_rooms(self, rooms): self.rooms = rooms; print(f"\nROOMS:\n {rooms}\n")

    def get_state_configurations(self, state_configurations): 
        self.state_configurations = state_configurations
        self.idle_conf = state_configurations[0]
        self.active_conf = state_configurations[1]
        self.medication_taken_conf = state_configurations[2]
        self.medication_missed_conf = state_configurations[3]
        self.alert_conf = state_configurations[4]
        print(f"\nALERT CONFS:\n {state_configurations}\n")

    def get_medication_schedules(self,schedules): self.schedules = schedules; print(f"\nSCHEDULES:\n {schedules}\n")

    def change_state(self, state: 'State'):
        self.state = state
        self.state.handle()

    def update(self):
        self.state.handle()
        #print(self.state.__class__.__name__)
    
    def get_reminder_datetime(self, schedule):
        current_date = datetime.now().date()
        return datetime.strptime(f"{current_date} {schedule.reminder_time}", "%Y-%m-%d %H:%M:%S")

    def get_end_datetime(self, schedule):
        reminder_datetime = self.get_reminder_datetime(schedule)
        return reminder_datetime + timedelta(hours=schedule.time_window)

    def is_medication_time(self):
        current_datetime = datetime.now()
        for schedule in self.schedules:
            if self.get_reminder_datetime(schedule) <= current_datetime <= self.get_end_datetime(schedule):  # Current time is within the time window
                return True
        return False

    def is_medication_time_passed(self):
        current_datetime = datetime.now()
        for schedule in self.schedules:
            end_datetime = self.get_end_datetime(schedule)
            missed_window_end = end_datetime + timedelta(hours=1)
            if end_datetime < current_datetime <= missed_window_end:  # Current time is within the missed window
                if not self.is_medication_time():  # Check if no other schedule is active
                    return True
        return False
    
    def apply_config(self, config: StateConfig, room = None):
        if config.color_code:
            color = hex_to_rgb(config.color_code)
            event_system.publish(EventType.CHANGE_COLOR, DeviceEvent(room=room, color=color))
        if config.blink:
            pass
        if config.sound_file:
            event_system.publish(EventType.PLAY_SOUND, config.sound_file)
 
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

    def setup(self):
        #conf: StateConfig = self.reminder_system.idle_conf
        #if conf.color_code is not None or conf.color_code != "#000000":
        #    event_system.publish(EventType.REMIND_EVERYWHERE, conf)
        self.x = 0
        #event_system.publish(EventType.BLINK_TIMES, DeviceEvent(blink_times=2, blink_interval=2))
        print("fuck")
        #event_system.publish(EventType.BLINK_TIMES, DeviceEvent(blink_times=2, blink_interval=2))
        event_system.publish(EventType.START_BLINK, DeviceEvent(blink_interval=2))


    def handle(self):
        if self.reminder_system.is_medication_time() and False:
            self.reminder_system.change_state(ActiveState(self.reminder_system))
        sleep(1)
        if self.x % 2 == 0:
            pass
            #print("turn on 1")
            #event_system.publish(EventType.TURN_ON, DeviceEvent)
            #event_system.publish(EventType.CHANGE_COLOR, DeviceEvent(color={"r":46,"g":102,"b":150}))
        else:
            #event_system.publish(EventType.CHANGE_COLOR, DeviceEvent(color={"r":200,"g":75,"b":56}))
            #event_system.publish(EventType.TURN_OFF, DeviceEvent)
            #print("turn off 1")
            pass
        if self.x == 6:
            event_system.publish(EventType.STOP_BLINK, DeviceEvent())

        self.x+=1

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

    def handle(self):
        pass

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