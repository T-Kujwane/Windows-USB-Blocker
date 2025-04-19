from pystray import Icon, Menu, MenuItem
from PIL import Image
import sys

class SystemTrayInterface:
    def __init__(self, icon_name = "System Tray Icon", image_path = "sys_tray_icon.png", process = None):
        self.icon_name = icon_name
        self.image_path = image_path
        self.icon = None
        self.process = process

    def quit_application(self):
        self.icon.stop()
        if self.process:
            self.process.terminate()
            print(f"Process with PID {self.process.pid} terminated.")

    def create_image(self):
        # Load the image from the file
        try:
            return Image.open(self.image_path)
        except FileNotFoundError:
            print(f"Error: '{self.image_path}' not found.")
            sys.exit(1)
            
    def set_process(self, process):
        self.process = process

    def run(self):
        # Define the menu
        menu = Menu(
            MenuItem("Quit", self.quit_application)
        )

        # Create the icon
        self.icon = Icon(self.icon_name, self.create_image(), menu=menu)

        # Run the icon
        self.icon.run()

# Example usage
if __name__ == "__main__":
    app = SystemTrayInterface()
    app.run()