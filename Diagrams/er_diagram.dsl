Table MedicationSchedule {
  schedule_id UUID [pk]
  user_id UUID
  medication_name varchar(100)
  reminder_time time
  time_window int
  dosage varchar(100)
  instructions text
}

Table Room {
  room_id UUID [pk]
  user_id UUID [null]
  name varchar(100)
  connected_rooms list
}

Table Device {
  device_id UUID [pk]
  user_id UUID [null]
  zigbee_id varchar(50)
  name varchar(100)
  type varchar(6)
  status varchar(50)
  room_id UUID
}

Table AlertConfiguration {
  alert_id varchar(100) [pk]
  user_id UUID [null]
  alert_type varchar(5)
  color_code varchar(7)
  sound_file varchar
  room_id UUID
}

Table MQTTConfiguration {
  mqtt_id varchar(100) [pk]
  user_id UUID
  broker_address url
  port int
  username varchar(100) [null]
  password varchar(100) [null]
}

Table HeucodEvent {
  id UUID [pk]
  user_id UUID
  event_type varchar(100)
  event_type_enum int
  description text
}

Table User {
  id UUID [pk]
  username varchar(100)
  password varchar(100)
}

Ref: MedicationSchedule.user_id > User.id
Ref: Room.user_id > User.id
Ref: Device.user_id > User.id
Ref: Device.room_id > Room.room_id
Ref: AlertConfiguration.user_id > User.id
Ref: AlertConfiguration.room_id > Room.room_id
Ref: MQTTConfiguration.user_id > User.id
Ref: HeucodEvent.user_id > User.id



