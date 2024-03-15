import requests
from Serializer import HeucodEventSerializer
from heucod import HeucodEvent
from typing import Union, List

class DatabaseManager:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token

    def send_event(self, heucod_event: Union[HeucodEvent, List[HeucodEvent]]):
        headers = {'Authorization': f'Token {self.api_token}', 'Content-Type': 'application/json'}

        # If it's a single HeucodEvent, make it a list for uniform processing
        if not isinstance(heucod_event, list):
            heucod_event = [heucod_event]

        responses = []
        for event in heucod_event:
            serialized_data = HeucodEventSerializer.serialize(event)
            response = requests.post(self.api_url, data=serialized_data, headers=headers)
            responses.append(response)

        # Return a list of responses if there are multiple events, otherwise just a single response
        return responses if len(responses) > 1 else responses[0]
    



