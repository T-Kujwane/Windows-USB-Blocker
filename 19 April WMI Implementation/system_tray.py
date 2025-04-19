from pystray import Icon, Menu, MenuItem
from PIL import Image
import sys
from PyQt5.QtWidgets import QApplication, QInputDialog

class SystemTrayApp:
    def __init__(self, icon_name, image_path, override_code="mecio"):
        # Initialize the override code and attempts log
        self.icon_name = icon_name
        self.image_path = image_path
        self.icon = None
        self.OVERRIDE_CODE = override_code

    def quit_application(self, icon, item):
        def prompt_override_code():
            app = QApplication(sys.argv)
            code, ok = QInputDialog.getText(None, "Override Code", "Enter the override code:")
            if ok:
                return code
            return None

        entered_code = prompt_override_code()
        if entered_code == self.OVERRIDE_CODE:
            print("Override code accepted. Quitting application.")
        else:
            print("Invalid override code. Application will not quit.")
            return
        # Quit the application
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