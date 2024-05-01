import bluetooth
import subprocess
import time

def connect_device(address):
    # Try to connect several times
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(['bluetoothctl', 'connect', address], check=True, text=True, capture_output=True)
            if "Connection successful" in result.stdout:
                print(f"Successfully connected to {address}")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)  # wait before retrying
    return False

def find_and_play_audio(scan_duration=8, num_scans=3, audio_file='BabyElephantWalk60.wav'):
    discovered_devices = set()

    for i in range(num_scans):
        print(f"Scanning #{i+1}/{num_scans} for Bluetooth devices...")
        try:
            current_scan = bluetooth.discover_devices(
                duration=scan_duration,
                lookup_names=True,
                flush_cache=True,
                lookup_class=False
            )
            discovered_devices.update(current_scan)
            print(f"Found {len(current_scan)} devices this scan.")
        except Exception as e:
            print(f"An error occurred during scanning: {e}")
        time.sleep(5)

    if discovered_devices:
        print(f"Total unique devices found: {len(discovered_devices)}")
        for addr, name in discovered_devices:
            print(f"Attempting to connect to {name} - {addr}")
            if connect_device(addr):
                # Play audio using aplay or another suitable audio player
                try:
                    subprocess.run(['aplay', '-D', f'bluealsa:DEV={addr}', audio_file], check=True)
                    print(f"Audio playback attempted on {name}.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to play audio on {addr}: {e}")
            else:
                print(f"Failed to connect to {addr}.")
    else:
        print("No devices found.")

if __name__ == "__main__":
    find_and_play_audio()
