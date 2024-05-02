from enum import Enum
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from Database.Models import StateConfig, DeviceEvent
from time import sleep
from random import randint
'''
This Python module defines the core logic of the remind mechanisms. The system is structured around a state machine pattern,
allowing it to transition between various states based on medication schedules, user interactions, and system events.
'''
def log(message):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as "%H:%M:%S"
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"[{formatted_time}] {message}")

def hex_to_rgb(hex_color: str) -> dict:
    hex_color = hex_color.lstrip('#')

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return {"r": r, "g": g, "b": b}

class ReminderSystem:
    '''Initializes the system state, handles state changes. Retrieves data from the db through events'''
    def __init__(self):
        self.room_configurations = {} 
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

    def get_rooms(self, rooms): 
        self.rooms = rooms; 
        self.latest_room = rooms[0].room_id
        print(f"\nROOMS:\n {rooms}\n")

    def get_state_configurations(self, state_configurations): 
        self.state_configurations = state_configurations
        self.idle_conf = state_configurations[0]
        self.active_conf = state_configurations[4]
        self.medication_taken_conf = state_configurations[1]
        self.medication_missed_conf = state_configurations[2]
        self.alert_conf = state_configurations[3]
        print(f"\nALERT CONFS:\n {state_configurations}\n")

    def get_medication_schedules(self,schedules): self.schedules = schedules; print(f"\nSCHEDULES:\n {schedules}\n")

    def change_state(self, new_state: 'State'):
        if type(self.state) is type(new_state) or self.state == new_state:
            log(f"Attempted to change to the same type of state: {type(new_state).__name__}. No action taken.")
        else:
            log(f"Changing state from {type(self.state).__name__} to {type(new_state).__name__}")
            self.state = new_state

    def update(self):
        self.state.handle()
        log(self.state.__class__.__name__)
    
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

    def is_x_time_passed_since_medication_time(self, x):
        current_datetime = datetime.now()
        for schedule in self.schedules:
            end_datetime = self.get_end_datetime(schedule)
            missed_window_end = end_datetime + timedelta(hours=x)
            if end_datetime < current_datetime <= missed_window_end:  # Current time is within the missed window
                if not self.is_medication_time():  # Check if no other schedule is active
                    return True
        return False

    def activate_room(self, config: StateConfig, room=None):
        current_config = self.room_configurations.get(room)
        if current_config == config:
            log(f"{room} is already activated with the given configuration. No action taken.")
            return

        log(f'ACTIVATE {room}, with {config.state_name}')
        event_system.publish(EventType.TURN_ON, DeviceEvent(room=room))
        if config.color_code:
            color = hex_to_rgb(config.color_code)
            event_system.publish(EventType.CHANGE_COLOR, DeviceEvent(room=room, color=color))
        if config.blink:
            interval = config.blink_interval if config.blink_interval else 1
            if config.blink_times:
                event_system.publish(EventType.BLINK_TIMES, DeviceEvent(room=room, blink_interval=interval, blink_times=config.blink_times))
            else:
                event_system.publish(EventType.START_BLINK, DeviceEvent(room=room, interval=interval))
        if config.sound_file:
            event_system.publish(EventType.PLAY_SOUND, config.sound_file)
        
        # Update the room's current configuration after activation
        self.room_configurations[room] = config

    def deactivate_room(self, room=None):
        log(f'DEACTIVATING ROOM: {room}')
        event_system.publish(EventType.TURN_OFF, DeviceEvent(room=room))
        event_system.publish(EventType.STOP_BLINK, DeviceEvent(room=room))
        event_system.publish(EventType.STOP_SOUND, DeviceEvent(room=room))
        
        # Reset the room's configuration upon deactivation
        if room in self.room_configurations:
            del self.room_configurations[room]

 
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
        log("Entering Idle State")
        for room in self.reminder_system.rooms:
            self.reminder_system.activate_room(self.reminder_system.idle_conf, room.room_id)
        event_system.publish(EventType.PLAY_SOUND, self.reminder_system.idle_conf.sound_file)

    def handle(self):
        if self.reminder_system.is_medication_time() and False:
            self.reminder_system.change_state(ActiveState(self.reminder_system))

class ActiveState(State):
    def setup(self):
        log("Entering Active State")
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.ROOM_EMPTY, self.reminder_system.deactivate_room)
        self.reminder_system.activate_room(self.reminder_system.active_conf, self.reminder_system.latest_room)

    def get_motion_alert(self, room):
        self.reminder_system.activate_room(self.reminder_system.active_conf, room)

    def medication_event(self, data):
        self.reminder_system.change_state(MedicationTakenState(self.reminder_system))

    def handle(self):
        if self.reminder_system.is_x_time_passed_since_medication_time(1):
            self.reminder_system.change_state(MedicationMissedState(self.reminder_system))
        
class MedicationTakenState(State):
    def setup(self):
        log("Entering Medication Taken State")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.ROOM_EMPTY, self.reminder_system.deactivate_room)
        self.reminder_system.activate_room(self.reminder_system.medication_taken_conf, self.reminder_system.latest_room)
        self.n_meds = 0

    def get_motion_alert(self, room):
        self.reminder_system.activate_room(self.reminder_system.medication_taken_conf, room)

    def medication_event(self, data):
        self.n_meds += 1
        if self.n_meds > 4:
            self.reminder_system.change_state(AlertState(self.reminder_system))
        log(f'Number of meds taken ~{self.n_meds}')
 
    def handle(self):
        if not self.reminder_system.is_x_time_passed_since_medication_time(1) or not self.reminder_system.is_medication_time():
            self.reminder_system.change_state(IdleState(self.reminder_system))

class MedicationMissedState(State):
    def setup(self):
        log("Entering Medication Missed State")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.ROOM_EMPTY, self.reminder_system.deactivate_room)
        self.reminder_system.activate_room(self.reminder_system.medication_missed_conf, self.reminder_system.latest_room)

    def medication_event(self, data):
        self.reminder_system.change_state(MedicationTakenState(self.reminder_system))

    def get_motion_alert(self, room):
        self.reminder_system.activate_room(self.reminder_system.medication_missed_conf, room)

    def handle(self):
        if not self.reminder_system.is_x_time_passed_since_medication_time(1) or not self.reminder_system.is_medication_time():
            self.reminder_system.change_state(IdleState(self.reminder_system))

class AlertState(State):
    def setup(self):
        log("Entering Alert State")
        for room in self.reminder_system.rooms:
            self.reminder_system.activate_room(self.reminder_system.alert_conf, room.room_id)
        event_system.publish(EventType.NOTIFY_CAREGIVER,"Medication Taken again")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.ALERT_RESOLVED,self.alert_resolved)
        self.number_of_meds_taken = 2
    
    def alert_resolved(self,data):
        self.reminder_system.change_state(IdleState(self.reminder_system))

    def medication_event(self, data):
        self.number_of_meds_taken += 1
        if self.number_of_meds_taken > 10:
            event_system.publish(EventType.NOTIFY_CAREGIVER,f"FUCK FUCK FUCK {self.number_of_meds_taken}")
            return
        elif self.number_of_meds_taken > 50:
            event_system.publish(EventType.NOTIFY_CAREGIVER,f"HE DEAD {self.number_of_meds_taken}")
            return
        event_system.publish(EventType.NOTIFY_CAREGIVER,f"WE HAVE A PROBLEM {self.number_of_meds_taken}")

    def handle(self):
        pass