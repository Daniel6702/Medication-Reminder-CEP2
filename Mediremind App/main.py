from time import sleep
from MQTTController import Cep2Controller

controller = Cep2Controller()
controller.start()

print("Waiting for events...")

while True:
    sleep(1)

controller.stop()