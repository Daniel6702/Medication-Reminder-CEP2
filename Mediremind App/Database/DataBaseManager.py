import requests
from heucod import HeucodEvent
from typing import Union, List
import json
from heucod import HeucodEvent, HeucodEventJsonEncoder
import Models
import threading
import time

class HeucodEventSerializer:
    @staticmethod
    def serialize(heucod_event: HeucodEvent) -> str:
        return json.dumps(heucod_event, cls=HeucodEventJsonEncoder)

    @staticmethod
    def deserialize(json_data: str) -> HeucodEvent:
        return HeucodEvent.from_json(json_data)

class DatabaseManager:
    def __init__(self, base_api_url: str, api_token: str):
        self.instance = DatabaseManager.Instance(self)
        if base_api_url.endswith('/'):
            self.base_api_url = base_api_url[:-1]
        else:
            self.base_api_url = base_api_url
        self.api_token = api_token

    def send_heucod_event(self, heucod_event: Union[HeucodEvent, List[HeucodEvent]]) -> list[requests.Response]:
        headers = {'Authorization': f'Token {self.api_token}', 'Content-Type': 'application/json'}

        if not isinstance(heucod_event, list):
            heucod_event = [heucod_event]

        responses = []
        for event in heucod_event:
            serialized_data = HeucodEventSerializer.serialize(event)
            response = requests.post(self.base_api_url + '/api/heucod-event/', data=serialized_data, headers=headers)
            responses.append(response)

        return responses
    
    def get_medication_schedules(self) -> List[Models.MedicationSchedule]:
        headers = {'Authorization': f'Token {self.api_token}'}
        response = requests.get(self.base_api_url + '/api/medication-schedule/', headers=headers)
        schedules = []
        for schedule in response.json():
            schedules.append(Models.MedicationSchedule.from_json(schedule))
        return schedules
    
    def get_mqtt_configuration(self) -> Models.MQTTConfiguration:
        headers = {'Authorization': f'Token {self.api_token}'}
        response = requests.get(self.base_api_url + '/api/mqtt-configuration/', headers=headers)
        return Models.MQTTConfiguration.from_json(response.json())
    
    def get_alert_configuration(self) -> List[Models.AlertType]:
        pass

    def get_rooms(self) -> List[Models.Room]:
        pass

    def get_devices(self) -> List[Models.Device]:
        pass

    class Instance:
        def __init__(self, database_manager: 'DatabaseManager'):
            self.__database_manager = database_manager
            self.medication_schedules = None
            self.alert_configurations = None
            self.mqtt_configuration = None
            self.rooms = None
            self.devices = None
            self.__update_thread = threading.Thread(target=self.__background_update, daemon=True)
            self.__update_thread.start()

        def __background_update(self):
            while True:
                self.update()
                time.sleep(1800)

        def update(self):
            self.medication_schedules = self.__database_manager.get_medication_schedules()
            self.alert_configurations = self.__database_manager.get_alert_configuration()
            self.mqtt_configuration = self.__database_manager.get_mqtt_configuration()
            self.rooms = self.__database_manager.get_rooms()
            self.devices = self.__database_manager.get_devices()
