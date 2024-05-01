#Database connection
base_api_url = 'http://localhost:8000'
api_token = '43ac84fbf3d368611f60dd24d878fe9f6b5ce635'

#currently the system periodically retrieves the configuration data from the database. 
#This isnt ideal since if the conf is modified in the ui it could take up to 'x' time for the system to update.
#Frequent updates strains the api
AUTO_UPDATE = False
UPDATE_TIME = 1800 #seconds

#Mqtt2Zigbee connection
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883

#Device identification. Device events from z2m does not implicitly state the device type. 
#These rules are used to determine the type from the msg string
DEVICE_TYPES = {
    'RGB_STRIP': {
        'must_have': ['color', 'state'], 
        'or_must_have': ['color_mode'],
    },
    'PIR_SENSOR': {
        'or_must_have': ['illuminance','illuminance_lux','occupancy'],
    },
    'SWITCH': {
        'or_must_have': ['ON', 'OFF'],
        'must_not_have': ['color']
    },
    'VIBRATION_SENSOR': {
        'must_have': ['angle', 'angle_x', 'angle_y'],
        'or_must_have': ['vibration'],
    }
}
#must_have_all. 
#or_must_have
#must_have_any
#must_not_have

EVENT_SENDING_TIME = 15 #minutes