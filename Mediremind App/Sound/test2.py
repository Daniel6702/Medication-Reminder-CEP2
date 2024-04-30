import sys
import time
import pexpect
import subprocess

class BluetoothctlError(Exception):
    """Exception raised when bluetoothctl fails to start."""
    pass


class MusicPlayer:
    """Simple music player class to simulate audio playback."""
    def play(self, mac_address):
        print(f"Simulating playing music on {mac_address}")

class BluetoothSpeakerManager:
    """Class to auto pair, trust, and connect with a Bluetooth speaker."""
    DEVICE_CONNECT_SUCCESS_MESSAGE = "dev_connect successful"

    def __init__(self, device_mac_addresses, music_player: MusicPlayer):
        self.device_mac_addresses = device_mac_addresses
        self.music_player = music_player
        self.device_is_not_connected = True
        
        # Unblock Bluetooth to ensure it's not disabled
        subprocess.check_output("/usr/sbin/rfkill unblock bluetooth", shell=True)
        # Create a child process to interact with bluetoothctl
        self.child = pexpect.spawn("bluetoothctl", echo=False)
        self.configure_bluetooth()

    def configure_bluetooth(self):
        """Configure Bluetooth to be discoverable and pairable."""
        self.run_command("power on")
        self.run_command("discoverable on")
        self.run_command("pairable on")

    def run_command(self, command, response="succeeded"):
        """Send a command to bluetoothctl."""
        self.child.sendline(command)
        if self.child.expect([response, pexpect.EOF, pexpect.TIMEOUT], timeout=5) != 0:
            raise BluetoothctlError(f"Failed to execute '{command}'")

    def connect_to_speakers(self):
        """Attempt to connect to Bluetooth speakers until successful or list exhausted."""
        while self.device_is_not_connected:
            for mac_address in self.device_mac_addresses:
                try:
                    print(f"Trying to connect to {mac_address}")
                    result = subprocess.run(["/usr/local/bin/auto-agent", mac_address], capture_output=True, text=True)
                    print(f"Output from auto-agent for device {mac_address}:\n{result.stdout}")
                    if self.DEVICE_CONNECT_SUCCESS_MESSAGE in result.stdout:
                        print(f"Connection to {mac_address} successful")
                        self.device_is_not_connected = False
                        self.play_music(mac_address)
                        break
                    else:
                        print(f"Connection to {mac_address} failed")
                except Exception as e:
                    print(f"Error connecting to device {mac_address}: {e}")

    def play_music(self, mac_address):
        """Play music using an external music player setup."""
        if self.music_player:
            self.music_player.play(mac_address)

# Example usage
if __name__ == "__main__":
    device_mac_addresses = ["98:52:3D:44:E8:67"]  # Add your device's MAC address here
    music_player = MusicPlayer()
    bt_manager = BluetoothSpeakerManager(device_mac_addresses, music_player)
    bt_manager.connect_to_speakers()
