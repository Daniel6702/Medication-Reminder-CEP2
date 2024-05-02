from EventSystem import EventType, event_system
import pygame

class SoundController:
    def __init__(self):
        # Subscribe to event types
        event_system.subscribe(EventType.PLAY_SOUND, self.play_sound)
        event_system.subscribe(EventType.STOP_SOUND, self.stop_sound)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # This will keep track of whether something is playing
        self.is_playing = False

    def play_sound(self, data):
        if 'file_path' in data:
            # Load and play the sound file
            pygame.mixer.music.load(data['file_path'])
            pygame.mixer.music.play()
            self.is_playing = True
        else:
            print("No file path provided in data.")

    def stop_sound(self, data):
        # Stop the music if it is playing
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
