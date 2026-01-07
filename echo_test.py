import sys
from datetime import datetime
from remote.remote import SiriRemote, RemoteListener


class Callback(RemoteListener):
    def event_battery(self, percent: int):
        print(f"[{datetime.now}] Battery", percent)

    def event_power(self, charging: bool):
        print(f"[{datetime.now}] Charging", charging)

    def event_button(self, button: int):
        print(f"[{datetime.now}] Button", button)

    def event_touchpad(self, data):
        print(f"[{datetime.now}] Touch", data)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        mac = sys.argv[1]
        SiriRemote(mac, Callback())
    else:
        print("error: no mac address")
