import requests

from Serializer import HeucodEventSerializer
from heucod import HeucodEvent

class DatabaseManager:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token

    def send_event(self, heucod_event: HeucodEvent):
        serialized_data = HeucodEventSerializer.serialize(heucod_event)
        print(serialized_data)
        headers = {'Authorization': f'Token {self.api_token}', 'Content-Type': 'application/json'}
        response = requests.post(self.api_url, data=serialized_data, headers=headers)
        return response

