from DataBaseManager import DatabaseManager
from heucod import HeucodEvent

#This is a test file to test the database manager

api_url = 'http://localhost:8001/api/heucod-events/'
api_token = '43ac84fbf3d368611f60dd24d878fe9f6b5ce635'

db_manager = DatabaseManager(api_url, api_token)

from datetime import datetime
import uuid

# Timestamp conversion to integer
timestamp_str = "2024-03-14T10:00:00"
timestamp_obj = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
timestamp_int = int(timestamp_obj.timestamp())

# Generate a UUID for id (if required)
event_id = uuid.uuid4()

# Create an instance of HeucodEvent with appropriate data
heucod_event = HeucodEvent(
    id_=event_id,
    event_type="sensor_data",
    event_type_enum=80542, # Replace with the appropriate enum value
    description="Event description",
    timestamp=timestamp_int
    # Include other fields as necessary, especially if they are required
)

# Send the event
response = db_manager.send_event(heucod_event)
print(response.status_code, response.text)
