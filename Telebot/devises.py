from SonoffBasic.sonoff import Sonoff
import config

def devace(id, c):
    global device
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    print(sonoff.devices[c]['status'])
    if sonoff.devices[c]['status'] == 'off':
        print(1234567)
        sonoff.change_device_status(deviceid=id, new_status='on')
    if sonoff.devices[c]['status'] == 'on':
        print(213213)
        sonoff.change_device_status(deviceid=id, new_status='off')
