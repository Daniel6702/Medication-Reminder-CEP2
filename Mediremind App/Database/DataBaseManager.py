import requests
from typing import Union, List
import json
from .heucod import HeucodEvent, HeucodEventJsonEncoder
from . import Models
import threading
import time
from config import AUTO_UPDATE, UPDATE_TIME
from EventSystem import event_system, EventType
from dataclasses import asdict, is_dataclass
from enum import Enum
from datetime import datetime

class HeucodEventSerializer:
    @staticmethod
    def serialize(heucod_event: HeucodEvent) -> str:
        return json.dumps(heucod_event, cls=HeucodEventJsonEncoder)

    @staticmethod
    def deserialize(json_data: str) -> HeucodEvent:
        return HeucodEvent.from_json(json_data)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value  # Convert Enum to its value
        if is_dataclass(o):
            return asdict(o)  # Convert dataclass to dict
        if isinstance(o, datetime):
            return o.isoformat()  # Convert datetime to ISO format
        return super().default(o)

class DatabaseManager():
    '''
    Manages interactions with the database. Responsible for sending events, 
    retrieving medication schedules, MQTT configurations, and device details.
    '''
    class EventHandler():
        '''subscribes to various types of events and delegates the handling to the DatabaseManager methods.
        For instance, when a component makes a database request, this event handler, having subscribed to such requests, 
        executes the corresponding database method. It then publishes the response, 
        to which the requesting component is already subscribed, thus completing the communication cycle.'''
        def __init__(self, database_manager: 'DatabaseManager'):
            self.database_manager = database_manager
            event_system.subscribe(EventType.ADD_DEVICE, self.database_manager.add_device)
            event_system.subscribe(EventType.NOTIFICATION, self.database_manager.send_notification)
            event_system.subscribe(EventType.HEUCOD_EVENT, self.database_manager.send_heucod_event)
            event_system.subscribe(EventType.UPDATE_DB_INSTANCE, self.database_manager.instance.update)
            event_system.subscribe(EventType.UPDATE_DB_ATTRIBUTE, self.database_manager.instance.update_attribute)
            event_system.subscribe(EventType.REQUEST_SCHEDULES, self.make_request(self.database_manager.get_medication_schedules, self.database_manager.instance.medication_schedules,EventType.RESPONSE_SCHEDULES))
            event_system.subscribe(EventType.REQUEST_DEVICES, self.make_request(self.database_manager.get_devices, self.database_manager.instance.devices, EventType.RESPONSE_DEVICES))
            event_system.subscribe(EventType.REQUEST_MQTT_CONF, self.make_request(self.database_manager.get_mqtt_configuration, self.database_manager.instance.mqtt_configuration, EventType.RESPONSE_MQTT_CONF))
            event_system.subscribe(EventType.REQUEST_STATE_CONFS, self.make_request(self.database_manager.get_state_configs, self.database_manager.instance.alert_configurations, EventType.RESPONSE_STATE_CONFS))
            event_system.subscribe(EventType.REQUEST_ROOMS,self.make_request(self.database_manager.get_rooms, self.database_manager.instance.rooms, EventType.RESPONSE_ROOMS))
            event_system.subscribe(EventType.SEND_EVENTS,self.database_manager.send_events)

        def make_request(self, new_method, old_method, response_type):
            '''When making a db request you can choose between fetching new data
            or using existing data based on the request type "new" or "old". 
            "new" performs an api call, "old" retrieves from the "Instance" class'''
            def request(data='old'):
                if data == 'new':
                    result = new_method()
                else:  
                    result = old_method
                event_system.publish(response_type, result)
            return request
        
    class Instance:
        '''       
        Represents an instance of the database state within the DatabaseManager. 
        Maintains local copies of various data elements and can update them.
        '''
        def __init__(self, database_manager: 'DatabaseManager'):
            self.__database_manager = database_manager
            self.medication_schedules = None
            self.alert_configurations = None
            self.mqtt_configuration = None
            self.rooms = None
            self.devices = None

            if AUTO_UPDATE:
                self.__update_thread = threading.Thread(target=self.__background_update, daemon=True)
                self.__update_thread.start()

        def __background_update(self):
            while True:
                self.update()
                time.sleep(UPDATE_TIME)

        def update_attribute(self, attribute_name: str):
            update_methods = {
                "medication_schedules": self.__database_manager.get_medication_schedules,
                "alert_configurations": self.__database_manager.get_state_configs,
                "mqtt_configuration": self.__database_manager.get_mqtt_configuration,
                "rooms": self.__database_manager.get_rooms,
                "devices": self.__database_manager.get_devices,
            }

            if attribute_name in update_methods:
                updated_value = update_methods[attribute_name]()
                setattr(self, attribute_name, updated_value)
            else:
                raise ValueError(f"Unknown attribute: {attribute_name}")

        def update(self):
            self.medication_schedules = self.__database_manager.get_medication_schedules()
            self.alert_configurations = self.__database_manager.get_state_configs()
            self.mqtt_configuration = self.__database_manager.get_mqtt_configuration()
            self.rooms = self.__database_manager.get_rooms()
            self.devices = self.__database_manager.get_devices()
            
    def __init__(self, base_api_url: str, api_token: str):
        self.base_api_url = base_api_url
        self.headers= {'Authorization': f'Token {api_token}'}
        self.instance = DatabaseManager.Instance(self)
        self.event_handler = DatabaseManager.EventHandler(self)

    def send_events(self, events: list):
        serialized_events = json.dumps(events, cls=EnhancedJSONEncoder)

        response = requests.post(
            self.base_api_url + '/api/event/',
            data=serialized_events,
            headers={**self.headers, 'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            print("Events Sent")
        else:
            print("Error sending Events:", response.text)

        return response

    def send_notification(self, notification: Models.Notification):
        serialized_notification= json.dumps(notification, cls=EnhancedJSONEncoder)

        response = requests.post(
            self.base_api_url + '/api/notification/', 
            data=serialized_notification, 
            headers={**self.headers, 'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            print("Notification Sent")
        else:
            print("Error sending Notification:", response.text)

        return response

    def get_medication_schedules(self) -> List[Models.MedicationSchedule]:
        response = requests.get(self.base_api_url + '/api/medication-schedule/', headers=self.headers)
        schedules = []
        for schedule in response.json():
            schedules.append(Models.MedicationSchedule.from_json(schedule))
        return schedules
    
    def get_mqtt_configuration(self) -> Models.MQTTConfiguration:
        response = requests.get(self.base_api_url + '/api/mqtt-configuration/', headers=self.headers)
        return Models.MQTTConfiguration.from_json(response.json())
    
    def get_state_configs(self) -> list[Models.StateConfig]:
        response = requests.get(self.base_api_url + '/api/state_config/', headers=self.headers)
        response.raise_for_status()  
        configs = [Models.StateConfig.from_json(conf) for conf in response.json()]
        return configs

    def get_rooms(self) -> list[Models.Room]:
        response = requests.get(self.base_api_url + '/api/room/', headers=self.headers)
        rooms = []
        for room in response.json():
            rooms.append(Models.Room.from_json(room))
        return rooms

    def send_heucod_event(self, heucod_event: Union[HeucodEvent, List[HeucodEvent]]) -> list[requests.Response]:
        headers = {**self.headers, 'Content-Type': 'application/json'}
        if not isinstance(heucod_event, list):
            heucod_event = [heucod_event]
        responses = []
        for event in heucod_event:
            serialized_data = HeucodEventSerializer.serialize(event)
            response = requests.post(self.base_api_url + '/api/heucod-event/', data=serialized_data, headers=headers)
            responses.append(response)

        return responses

    def get_devices(self) -> List[Models.Device]:
        response = requests.get(self.base_api_url + '/api/device/', headers=self.headers)
        devices = []
        for device in response.json():
            devices.append(Models.Device.from_json(device))
        return devices
    
    def add_device(self, device: Models.Device):
        if hasattr(device, 'status') and device.status is None:
            device.status = 'Default status'

        serialized_device = json.dumps(device, cls=EnhancedJSONEncoder)

        response = requests.post(
            self.base_api_url + '/api/device/', 
            data=serialized_device, 
            headers={**self.headers, 'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            print("Device successfully added.")
        else:
            print("Error adding device:", response.text)

        return response