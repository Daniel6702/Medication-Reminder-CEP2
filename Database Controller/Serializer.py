import json
from heucod import HeucodEvent, HeucodEventJsonEncoder

class HeucodEventSerializer:
    @staticmethod
    def serialize(heucod_event: HeucodEvent) -> str:
        # Convert a HeucodEvent instance to a JSON string
        return json.dumps(heucod_event, cls=HeucodEventJsonEncoder)

    @staticmethod
    def deserialize(json_data: str) -> HeucodEvent:
        # Convert a JSON string to a HeucodEvent instance
        return HeucodEvent.from_json(json_data)
