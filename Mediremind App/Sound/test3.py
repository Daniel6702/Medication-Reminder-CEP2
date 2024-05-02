import pygame

def play_audio(file_path):
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Load the sound file
    pygame.mixer.music.load(file_path)
    
    # Play the sound
    pygame.mixer.music.play()
    
    # Wait for the music to play completely
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Replace 'your_audio_file.mp3' with the path to your actual audio file
play_audio('test_sound_file.wav')
