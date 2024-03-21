'''
Database API Example
'''
from DataBaseManager import DatabaseManager
from heucod import HeucodEvent
from datetime import datetime
import uuid

#Create timestamp
timestamp_str = "2024-03-14T10:00:00"
timestamp_obj = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
timestamp_int = int(timestamp_obj.timestamp())

# Create HeucodEvents object with a unique ID, type, enum, etc.
sensor_data_event = HeucodEvent(
    id=str(uuid.uuid4()),  
    event_type="temperature_reading",
    event_type_enum=1001,
    description="Temperature sensor reading in room",
    timestamp=timestamp_int,
    sensor_id="sensor_12345",
    sensor_type="temperature",
    sensor_location="Room 101",
    value="22.5",
    unit="Celsius"
)

patient_alert_event = HeucodEvent(
    id=str(uuid.uuid4()),  
    event_type="patient_fall_detected",
    event_type_enum=2002,
    description="Patient fall detection alert",
    timestamp=timestamp_int,
    patient_id="patient_67890",
    location="Room 202",
    sensor_id="sensor_67890",
    sensor_type="motion",
    direct_event=True
)

device_status_event = HeucodEvent(
    id=str(uuid.uuid4()),  
    event_type="device_battery_low",
    event_type_enum=3003,
    description="Battery level low on device",
    timestamp=timestamp_int,
    device_model="Model X200",
    device_vendor="Vendor ABC",
    battery=15,  # Battery level in percentage
    sensor_id="sensor_54321"
)

environmental_data_event = HeucodEvent(
    id=str(uuid.uuid4()),  
    event_type="humidity_level",
    event_type_enum=4004,
    description="Humidity level reading in site area",
    timestamp=timestamp_int,
    sensor_id="sensor_112233",
    sensor_type="humidity",
    location="Site A",
    value="45",
    unit="%"
)

# API URL and token for accessing the database service.
base_api_url = 'http://localhost:8000'
api_token = '43ac84fbf3d368611f60dd24d878fe9f6b5ce635' #Specific for the user

# Initialize a database manager with the given API URL and token.
db_manager = DatabaseManager(base_api_url, api_token)

# Send the HeucodEvents to the database and store the response.
# send_event can take a single HeucodEvent or a list of HeucodEvents
#response = db_manager.send_heucod_event([sensor_data_event, patient_alert_event, device_status_event, environmental_data_event]) 

#medication_schedules = db_manager.get_medication_schedules()
conf = db_manager.get_mqtt_configuration()

print(conf)

#if isinstance(response, list):
#    for x in response:
#        print(x.status_code, x.text)
#else:
#    print(response.status_code, response.text)