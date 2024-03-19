import requests
from heucod import HeucodEvent
from typing import Union, List
import json
from heucod import HeucodEvent, HeucodEventJsonEncoder

class HeucodEventSerializer:
    @staticmethod
    def serialize(heucod_event: HeucodEvent) -> str:
        return json.dumps(heucod_event, cls=HeucodEventJsonEncoder)

    @staticmethod
    def deserialize(json_data: str) -> HeucodEvent:
        return HeucodEvent.from_json(json_data)

class DatabaseManager:
    def __init__(self, base_api_url: str, api_token: str):
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
    
    def get_medication_schedules(self) -> requests.Response:
        headers = {'Authorization': f'Token {self.api_token}'}
        response = requests.get(self.base_api_url + '/api/medication-schedule/', headers=headers)
        return response
    



