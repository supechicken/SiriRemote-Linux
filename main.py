import sys
import threading
import os
from remote.remote import SiriRemote, RemoteListener
from hid_input import Input

hid_input = Input()
mac = None
pointer_lock = False

class Callback(RemoteListener):
    def event_battery(self, percent: int):
        print("Battery", percent)

    def event_power(self, charging: bool):
        print("Charging", charging)

    def event_button(self, button: int):
        handle_button_event(button)

    def event_touchpad(self, data):
        handle_touchpad_event(data)


def disconnect_timer(event):
    pass
    #if not event.wait(6000):
    #    print('Disconnect!')
    #    os.system(f'bluetoothctl disconnect {mac}')

prevXY = [None, None]
disconnThread = [None, None]

def handle_touchpad_event(data):
    global disconnThread

    sensi = 4
    x = data[0] * sensi
    y = data[1] * - sensi * 2
    p = data[2]

    if not pointer_lock:
        return

    if prevXY[0] and prevXY[1]:
        offset_x = x - prevXY[0]
        offset_y = y - prevXY[1]

        if offset_x + offset_y != 0 and offset_x > -140:
            if offset_x + offset_y <= 5:
                hid_input.move_cursor(offset_x, offset_y)
            else:
                hid_input.move_cursor(int(offset_x * 1.3), int(offset_y * 1.3))

    if disconnThread[1] and disconnThread[1].is_alive():
        disconnThread[0].set()

    if p == 0:
        prevXY[0] = prevXY[1] = None

        disconnThread[0] = threading.Event()
        disconnThread[1] = threading.Thread(target=disconnect_timer, args=(disconnThread[0],))
        disconnThread[1].start()
    else:
        prevXY[0] = x
        prevXY[1] = y


def handle_button_event(button):
    global pointer_lock

    if disconnThread[1] and disconnThread[1].is_alive():
        disconnThread[0].set()

    if button == SiriRemote.BUTTON_RELEASED:
        hid_input.release()
        disconnThread[0] = threading.Event()
        disconnThread[1] = threading.Thread(target=disconnect_timer, args=(disconnThread[0],))
        disconnThread[1].start()
        return
    elif button & SiriRemote.BUTTON_SIRI:
        pointer_lock = not pointer_lock
        return

    if button & SiriRemote.BUTTON_POWER:
        hid_input.switch_uinput()

    if button & SiriRemote.BUTTON_UP:
        hid_input.add_key(Input.KEY_UP)

    if button & SiriRemote.BUTTON_DOWN:
        hid_input.add_key(Input.KEY_DOWN)

    if button & SiriRemote.BUTTON_LEFT:
        hid_input.add_key(Input.KEY_LEFT)

    if button & SiriRemote.BUTTON_RIGHT:
        hid_input.add_key(Input.KEY_RIGHT)

    if button & SiriRemote.BUTTON_TOUCHPAD:
        if pointer_lock:
            hid_input.add_key(Input.BTN_LEFT)
        else:
            hid_input.add_key(Input.KEY_ENTER)

    if button & SiriRemote.BUTTON_HOME:
        hid_input.add_key(Input.KEY_HOMEPAGE)

    if button & SiriRemote.BUTTON_VOLUME_UP:
        hid_input.add_key(Input.KEY_VOLUMEUP)

    if button & SiriRemote.BUTTON_VOLUME_DOWN:
        hid_input.add_key(Input.KEY_VOLUMEDOWN)

    if button & SiriRemote.BUTTON_BACK:
        hid_input.add_key(Input.KEY_BACK)

    if button & SiriRemote.BUTTON_MUTE:
        hid_input.add_key(Input.KEY_MUTE)

    if button & SiriRemote.BUTTON_PLAY_PAUSE:
        hid_input.add_key(Input.KEY_PLAYPAUSE)

    hid_input.press()


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            mac = sys.argv[1]
            SiriRemote(mac, Callback())
        else:
            print("error: no mac address")
    except KeyboardInterrupt:
        hid_input.close()
        exit()
