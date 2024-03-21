from time import sleep
from Cep2Controller import Cep2Controller
from Cep2Model import Cep2Model, Cep2ZigbeeDevice

ZB_ID = '0x680ae2fffe7242bc'

if __name__ == "__main__":
    # Create a data model and add a list of known Zigbee devices.

    #The model contains the zigbee devices
    devices_model = Cep2Model()

    #The model (devices) are added to the controller
    controller = Cep2Controller(devices_model)
    controller.start()  

    print("Waiting for events...")

    sleep(3)

    new_state = 'OFF'

    while True:
        if new_state == 'OFF':
            new_state = 'ON'
            controller._z2m_client.change_state(ZB_ID ,new_state)
        else:
            new_state = 'OFF'
            controller._z2m_client.change_state(ZB_ID, new_state)
        sleep(3)



    controller.stop()
