from EventSystem import EventType, event_system

class SoundController():
    def __init__(self):
        event_system.subscribe(EventType.PLAY_SOUND, self.play_sound)
        
    def play_sound(self, data):
        pass