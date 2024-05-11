from enum import Enum
from EventSystem import EventType, event_system
from Database.DataBaseManager import DatabaseManager
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from Database.Models import StateConfig, DeviceEvent, NotificationType
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
# The LGB strips differents colors: r = red, g = green & b = blue
def hex_to_rgb(hex_color: str) -> dict:
    hex_color = hex_color.lstrip('#')

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return {"r": r, "g": g, "b": b}

class ReminderSystem:
    '''Initializes the system state, handles state changes. Retrieves data from the db through events'''
    def __init__(self):
        # Initialize Reminder System
        self.room_configurations = {} 
        self.setup_connections()
        self.initialize_data()
        self.state = IdleState(self)

    def initialize_data(self):
        ''' Publish events to request initial data load.'''
        event_system.publish(EventType.REQUEST_ROOMS, 'new')
        event_system.publish(EventType.REQUEST_STATE_CONFS, 'new')
        event_system.publish(EventType.REQUEST_SCHEDULES, 'new')

    def setup_connections(self):
        # Subscribe to event responses
        event_system.subscribe(EventType.RESPONSE_ROOMS,self.get_rooms)
        event_system.subscribe(EventType.RESPONSE_STATE_CONFS,self.get_state_configurations)
        event_system.subscribe(EventType.RESPONSE_SCHEDULES, self.get_medication_schedules)

    def get_rooms(self, rooms): 
        # Handle response for room data retrieval
        self.rooms = rooms; 
        self.latest_room = rooms[0].room_id
        print(f"\nROOMS:\n {rooms}\n")

    def get_state_configurations(self, state_configurations): 
        # Handle response for state configuration data retrieval
        self.state_configurations = state_configurations
        self.idle_conf = state_configurations[0]
        self.active_conf = state_configurations[4]
        self.medication_taken_conf = state_configurations[1]
        self.medication_missed_conf = state_configurations[2]
        self.alert_conf = state_configurations[3]
        print(f"\nALERT CONFS:\n {state_configurations}\n")

    def get_medication_schedules(self,schedules): 
        # Handle response for medication schedules data retrieval
        self.schedules = schedules; 
        print(f"\nSCHEDULES:\n {schedules}\n")

    def change_state(self, new_state: 'State'):
        # Change system state
        if type(self.state) is type(new_state) or self.state == new_state:
            log(f"Attempted to change to the same type of state: {type(new_state).__name__}. No action taken.")
        else:
            log(f"Changing state from {type(self.state).__name__} to {type(new_state).__name__}")
            self.state = new_state

    def update(self):
         # Update system state
        self.state.handle()
        log(self.state.__class__.__name__)
    
    def get_reminder_datetime(self, schedule):
        # Calculate reminder datetime based on schedule
        current_date = datetime.now().date()
        return datetime.strptime(f"{current_date} {schedule.reminder_time}", "%Y-%m-%d %H:%M:%S")

    def get_end_datetime(self, schedule):
        # Calculate end datetime based on schedule
        reminder_datetime = self.get_reminder_datetime(schedule)
        return reminder_datetime + timedelta(hours=schedule.time_window)

    def is_medication_time(self):
         # Check if it's medication time
        current_datetime = datetime.now()
        for schedule in self.schedules:
            if self.get_reminder_datetime(schedule) <= current_datetime <= self.get_end_datetime(schedule):  # Current time is within the time window
                return True
        return False

    def is_x_time_passed_since_medication_time(self, x):
        # Check if x time has passed since medication time
        current_datetime = datetime.now()
        for schedule in self.schedules:
            end_datetime = self.get_end_datetime(schedule)
            missed_window_end = end_datetime + timedelta(hours=x)
            if end_datetime < current_datetime <= missed_window_end:  # Current time is within the missed window
                if not self.is_medication_time():  # Check if no other schedule is active
                    return True
        return False

    def activate_room(self, config: StateConfig, room=None):
        # Activate room with specified configuration
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
        # Deactivate specified room
        log(f'DEACTIVATING ROOM: {room}')
        event_system.publish(EventType.TURN_OFF, DeviceEvent(room=room))
        event_system.publish(EventType.STOP_BLINK, DeviceEvent(room=room))
        event_system.publish(EventType.STOP_SOUND, DeviceEvent(room=room))
        
        # Reset the room's configuration upon deactivation
        if room in self.room_configurations:
            del self.room_configurations[room]

    def reset_all_rooms(self):
        # Reset all rooms
        for room in self.rooms:
            self.deactivate_room(room.room_id)

    def activate_all_rooms(self, conf):
        # Activate all rooms with specified configuration
        for room in self.rooms:
            self.activate_room(room, conf)

class State(ABC):
    '''It provides a common interface for all states to implement the handle
    method and allows optional setup procedures for each state.'''
    def __init__(self, reminder_system: ReminderSystem):
         # Initialize State and call setup method
        self.reminder_system = reminder_system
        self.setup()

    @abstractmethod
    def handle(self):
        # don't know
        pass

    def setup(self):
        # don't know
        pass

class IdleState(State):
    '''Represents the idle state of the reminder system. It checks for medication times
    and changes to ActiveState if it's time for medication.'''

    def setup(self):  
        # Initialize timer and prepare reminder system for idle state
        self.timer = 0  
        log("Entering Idle State")
        self.reminder_system.reset_all_rooms()

        #temp
        event_system.publish(EventType.ALARM, True)
        

    def handle(self):
        # Check if it's time for medication
        if self.reminder_system.is_medication_time():
             # If the timer is less than 4 intervals, increment it
            if self.timer < 4:
                self.timer += 1
            else:
                # If the timer reaches 4 intervals, switch to Alert State and reset the timer
                #self.reminder_system.change_state(ActiveState(self.reminder_system))
                self.reminder_system.change_state(AlertState(self.reminder_system))
                self.timer = 0

class ActiveState(State):
    def setup(self):
        # Initialize Active State and set up event subscriptions, sound, and room reset
        log("Entering Active State")
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.ROOM_EMPTY, self.reminder_system.deactivate_room)
        event_system.publish(EventType.PLAY_SOUND, self.reminder_system.active_conf.sound_file)
        self.reminder_system.reset_all_rooms()

    def get_motion_alert(self, room):
        # Activate a specific room upon receiving a motion alert
        self.reminder_system.activate_room(self.reminder_system.active_conf, room)

    def medication_event(self, data):
        # Transition to MedicationTakenState upon receiving medication taken event
        self.reminder_system.change_state(MedicationTakenState(self.reminder_system))

    def handle(self):
        # If it's not medication time, transition to MedicationMissedState
        if not self.reminder_system.is_medication_time():
            self.reminder_system.change_state(MedicationMissedState(self.reminder_system))
        
class MedicationTakenState(State):
     # Initialize Medication Taken State and set up event subscriptions, sound, and room reset
    def setup(self):
        log("Entering Medication Taken State")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.ROOM_EMPTY, self.reminder_system.deactivate_room)
        event_system.publish(EventType.PLAY_SOUND, self.reminder_system.medication_taken_conf.sound_file)
        self.reminder_system.reset_all_rooms()
        self.n_meds = 0

    def get_motion_alert(self, room):
         # Activate specific room on motion alert
        self.reminder_system.activate_room(self.reminder_system.medication_taken_conf, room)

    def medication_event(self, data):
        # Increment medication counter, transition to AlertState if count exceeds 4
        self.n_meds += 1
        if self.n_meds > 4:
            self.reminder_system.change_state(AlertState(self.reminder_system))
        log(f'Number of meds taken ~{self.n_meds}')
 
    def handle(self):
        # Transition to IdleState if it's not medication time
        if not self.reminder_system.is_medication_time():
            self.reminder_system.change_state(IdleState(self.reminder_system))

class MedicationMissedState(State):
    def setup(self):
         # Initialize Medication Missed State and set up event subscriptions, notifications, sound, and room reset
        log("Entering Medication Missed State")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.MOTION_ALERT, self.get_motion_alert)
        event_system.subscribe(EventType.ROOM_EMPTY, self.reminder_system.deactivate_room)
        event_system.publish(EventType.SEND_NOTIFICATION, ["Medication missed", NotificationType.IMPORTANT])
        event_system.publish(EventType.PLAY_SOUND, self.reminder_system.medication_missed_conf.sound_file)
        self.reminder_system.reset_all_rooms()

    def medication_event(self, data):
        # Transition to MedicationTakenState on medication event
        self.reminder_system.change_state(MedicationTakenState(self.reminder_system))

    def get_motion_alert(self, room):
        # Activate specific room on motion alert
        self.reminder_system.activate_room(self.reminder_system.medication_missed_conf, room)

    def handle(self):
        # Transition to IdleState if it's not medication time and not enough time has passed since the last medication
        if not self.reminder_system.is_x_time_passed_since_medication_time(1) and not self.reminder_system.is_medication_time():
            self.reminder_system.change_state(IdleState(self.reminder_system))

class AlertState(State):
    def setup(self):
        # Initialize Alert State and set up event subscriptions, sound, and initial state variables
        log("Entering Alert State")
        event_system.publish(EventType.NOTIFY_CAREGIVER,"Medication Taken again")
        event_system.subscribe(EventType.MEDICATION_TAKEN, self.medication_event)
        event_system.subscribe(EventType.ALERT_RESOLVED,self.alert_resolved)
        event_system.publish(EventType.PLAY_SOUND, self.reminder_system.alert_conf.sound_file)
        event_system.subscribe(EventType.RESPONSE_ALARM_STATE, self.get_alert_state)
        #self.reminder_system.activate_all_rooms(self.reminder_system.alert_conf)
        self.number_of_meds_taken = 2
        self.timer = 0

    def get_alert_state(self, alarmed_state):
        # Transition to IdleState if the alarm state is resolved
        if alarmed_state is False:
            self.reminder_system.change_state(IdleState(self.reminder_system))
    
    def alert_resolved(self,data):
        # Transition to IdleState when the alert is resolved
        self.reminder_system.change_state(IdleState(self.reminder_system))

    def medication_event(self, data):
         # Handle medication events and notify caregiver
        self.number_of_meds_taken += 1
        if self.number_of_meds_taken > 10:
            event_system.publish(EventType.NOTIFY_CAREGIVER,f"FUCK FUCK FUCK {self.number_of_meds_taken}")
            return
        elif self.number_of_meds_taken > 50:
            event_system.publish(EventType.NOTIFY_CAREGIVER,f"HE DEAD {self.number_of_meds_taken}")
            return
        event_system.publish(EventType.NOTIFY_CAREGIVER,f"WE HAVE A PROBLEM {self.number_of_meds_taken}")

    def handle(self):
        # Increment timer and request alarm state update periodically
        if self.timer < 5:
            self.timer += 1
        else:
            self.timer = 0
            event_system.publish(EventType.REQUEST_ALARM_STATE, 'new')
