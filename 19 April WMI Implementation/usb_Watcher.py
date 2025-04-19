import wmi #type: ignore
import sys

# Connect to the WMI service
# c = wmi.WMI()

# Enumerate all USB devices
# Drive type = 2 means removable devices
# usb_devices = c.Win32_LogicalDisk(DriveType=2)

# for device in usb_devices:
#     print("Removable device found:", device.DeviceID)
#     print("Volume name:", device.VolumeName)
#     print("File system:", device.FileSystem)

# Setup a WMI event watcher for USB device insertion
# usb_insertion_watcher = c.Win32_VolumeChangeEvent.watch_for("Creation")
# print("Watching for USB device insertions...")

# usb_insertion = usb_insertion_watcher()
# print("USB device inserted:", usb_insertion.DriveName)

class USBWatcher:
    def __init__(self, c = wmi.WMI()):
        self.c = c
    
    def listen_for_usb_insertion(self):
        try:
            usb_insertion_watcher = self.c.Win32_VolumeChangeEvent.watch_for("Creation")
            while True:
                print("Watching for USB device insertions...")
                usb_insertion = usb_insertion_watcher()
                
                print(f"New USB Storage Device {usb_insertion.DriveName} inserted.")
        except KeyboardInterrupt as e:
            print("Process interrupted by user.")
            print(f"Error: {e}")
            sys.exit(0)

def main():
    usb_watcher = USBWatcher()
    usb_watcher.listen_for_usb_insertion()

if __name__ == "__main__":
    main()
