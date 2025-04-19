from pystray import Icon, Menu, MenuItem
from PIL import Image
import sys

class SystemTrayApp:
    def __init__(self, icon_name, image_path):
        self.icon_name = icon_name
        self.image_path = image_path
        self.icon = None

    def quit_application(self, icon, item):
        self.icon.stop()

    def create_image(self):
        # Load the image from the file
        try:
            return Image.open(self.image_path)
        except FileNotFoundError:
            print(f"Error: '{self.image_path}' not found.")
            sys.exit(1)

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
    app = SystemTrayApp("System Tray Icon", "sys_tray_icon.png")
    app.run()