import json
from heucod import HeucodEvent, HeucodEventJsonEncoder

class HeucodEventSerializer:
    @staticmethod
    def serialize(heucod_event: HeucodEvent) -> str:
        return json.dumps(heucod_event, cls=HeucodEventJsonEncoder)

    @staticmethod
    def deserialize(json_data: str) -> HeucodEvent:
        return HeucodEvent.from_json(json_data)
