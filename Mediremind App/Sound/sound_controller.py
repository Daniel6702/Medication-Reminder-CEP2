from EventSystem import EventType, event_system
import pygame
import requests
import tempfile
from urllib.parse import urlparse

class SoundController:
    def __init__(self):
        # Subscribe to event types
        event_system.subscribe(EventType.PLAY_SOUND, self.play_sound)
        event_system.subscribe(EventType.STOP_SOUND, self.stop_sound)

        pygame.mixer.init()

        self.is_playing = False

    def play_sound(self, data):
        print("hej")
        if self.is_playing:
            return
        print(f"PLAYING SOUND {data}")
        
        if urlparse(data).scheme in ['http', 'https']:
            # Download the file from the URL and play it
            response = requests.get(data)
            if response.status_code == 200:
                # Use a temporary file to save the audio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                    tmpfile.write(response.content)
                    pygame.mixer.music.load(tmpfile.name)
                    pygame.mixer.music.play()
                    self.is_playing = True
            else:
                print("Failed to download the file.")
        else:
            print("Invalid URL provided.")

    def stop_sound(self, data):
        # Stop the music if it is playing
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
