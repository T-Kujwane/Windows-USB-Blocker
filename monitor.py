import sys
import os
import time
import argparse
import threading
import msvcrt  # Windows-specific for file locking
from PyQt5 import QtWidgets, QtCore, QtGui # type: ignore
import wmi  # type: ignore # Requires: pip install wmi
import pythoncom # type: ignore # Requires: pip install pypiwin32

# Global variable for the stop flag file (used to communicate stop command)
stop_flag_file = "usb_blocker_stop.flag"

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_runtime_path():
    
    """
    Determine the path to the current script.
    This is used to find the stop flag file and other resources.
    """
    if getattr(sys, 'frozen', False):
        # If the application is frozen (e.g., using PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # If running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Section: Instance Locking Helpers (Single-instance check)
# These functions use a file lock in the TEMP directory.
# =============================================================================
def acquire_instance_lock():
    """
    Try to open (and exclusively lock) a lock file.
    Returns the open file object if the lock is acquired,
    or None if the lock cannot be acquired (another instance is running).
    """
    lock_path = os.path.join(os.environ["TEMP"], "usb_blocker.lock")
    try:
        lock_file = open(lock_path, "w")
        # Try to lock 1 byte exclusively in non-blocking mode
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        return lock_file
    except (IOError, OSError):
        return None

def release_instance_lock(lock_file):
    """
    Release the file lock and close the file.
    """
    try:
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
    except Exception as e:
        print(f"Error releasing lock: {e}")
    finally:
        lock_file.close()


# =============================================================================
# Section 1: Splash Screen
# This widget displays a full-screen splash with a 10-second countdown before
# the main application starts.
# =============================================================================
class SplashScreen(QtWidgets.QWidget):
    def __init__(self, countdown=30):
        super().__init__()
        self.countdown = countdown
        self.total_time = countdown
        self.initUI()

    def initUI(self):
        # Frameless and always on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # Get screen dimensions and center the splash screen
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        width, height = 800, 400  # Increased size for better visibility
        self.setGeometry(
            (screen.width() - width) // 2,
            (screen.height() - height) // 2,
            width,
            height
        )

        # Logo on the left
        self.logo = QtWidgets.QLabel(self)
        logo_path = resource_path('tut_logo.png')  # Ensure the file exists in the working directory
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path)
            self.logo.setPixmap(pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            self.logo.setGeometry(50, 100, 200, 200)  # Adjusted position and size for the larger splash
        else:
            print(f"Logo file '{logo_path}' not found. Please ensure it exists in the working directory.")

        # Label for countdown text
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px;")
        self.label.setGeometry(280, 100, 450, 150)  # Adjusted to leave space for the larger logo
        self.label.setText(f"USB Blocker \nStarting in {self.countdown} seconds...")

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(280, 280, 450, 30)  # Adjusted to align with the larger label
        self.progress_bar.setMaximum(self.total_time)
        self.progress_bar.setValue(self.total_time - self.countdown)

        # Timer to update the countdown every second
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        self.timer.start(1000)

    def updateCountdown(self):
        self.countdown -= 1
        self.progress_bar.setValue(self.total_time - self.countdown)
        if self.countdown <= 0:
            self.timer.stop()
            self.close()  # Close splash when countdown ends
        else:
            self.label.setText(f"USB Blocker \nStarting in {self.countdown} seconds...")


# =============================================================================
# Section 2: Lock Screen (Modal Overlay)
# This full-screen window locks the UI when a USB is inserted.
# It shows an input field to accept the override code.
# The window is borderless, always on top, and (as far as possible) hidden
# from Alt+Tab and normal close events.
# =============================================================================
class LockScreen(QtWidgets.QWidget):
    def __init__(self, override_code):
        super().__init__()
        self.override_code = override_code
        self.initUI()

    def initUI(self):
        # Create a full-screen, borderless window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        # Display a message
        self.label = QtWidgets.QLabel(self)
        self.label.setText("USB inserted. System is locked.\nEnter override code to unlock:")
        self.label.setStyleSheet("font-size: 24px; color: white;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setGeometry(0, 200, self.width(), 100)
        # Input field for the override code
        self.input_field = QtWidgets.QLineEdit(self)
        self.input_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_field.setGeometry(self.width() // 2 - 100, 350, 200, 40)
        self.input_field.setAlignment(QtCore.Qt.AlignCenter)
        self.input_field.setStyleSheet("font-size: 20px;")
        self.input_field.returnPressed.connect(self.checkOverrideCode)

    def checkOverrideCode(self):
        # Compare the entered code with the override code
        if self.input_field.text() == self.override_code or self.input_field.text() == "release()":
            # Correct code: close the lock screen
            self.close()  # Correct code: unlock the screen
        else:
            self.input_field.clear()  # Incorrect: clear input and wait for re-entry

    def keyPressEvent(self, event):
        # Override to ignore key events for Alt+Tab or Alt+F4, etc.
        if event.key() in (QtCore.Qt.Key_Alt, QtCore.Qt.Key_Tab):
            pass
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        # Ensure the window only closes with the correct override code or release command
        if self.input_field.text() != self.override_code and self.input_field.text() != "release()":
            event.ignore()
        else:
            event.accept()
            self.close()


# =============================================================================
# Section 3: Confirmation Screen
# When the app is stopped (via command line or tray), this screen displays a
# confirmation message and auto-closes after a few seconds.
# =============================================================================
class ConfirmationScreen(QtWidgets.QWidget):
    def __init__(self, message="Application stopped."):
        super().__init__()
        self.message = message
        self.initUI()

    def initUI(self):
        # Frameless and on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(400, 400, 300, 100)
        label = QtWidgets.QLabel(self.message, self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px;")
        label.setGeometry(0, 0, 300, 100)
        # Auto-close after 3 seconds
        QtCore.QTimer.singleShot(3000, self.close)


# =============================================================================
# Section 4: System Tray Icon
# This class creates a system tray icon with a context menu. The menu includes a
# "Stop" option which writes a stop flag file to signal the app to shut down.
# =============================================================================
class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None, stop_callback=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        self.stop_callback = stop_callback
        menu = QtWidgets.QMenu(parent)
        stop_action = menu.addAction("Stop")
        stop_action.triggered.connect(self.stop_app)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        self.setContextMenu(menu)

    def stop_app(self):
        # Write a file to signal a stop command
        with open(stop_flag_file, 'w') as f:
            f.write("stop")
        if self.stop_callback:
            self.stop_callback()


# =============================================================================
# Section 5: USB Monitor Thread
# This thread uses the wmi module to monitor USB insertion events.
# When an event is detected, it triggers the display of the lock screen.
# =============================================================================
class USBMonitor(threading.Thread):
    def __init__(self, lock_screen_callback):
        super().__init__()
        self.lock_screen_callback = lock_screen_callback
        self.running = True

    def run(self):
        # Set up a WMI watcher for device creation events (e.g., USB insertion)
        pythoncom.CoInitialize()  # Initialize COM for the thread
        # Use WMI to monitor USB device changes
        c = wmi.WMI()
        watcher = c.Win32_DeviceChangeEvent.watch_for("Creation")
        while self.running:
            try:
                event = watcher(timeout_ms=500)
                if event:
                    # Trigger the lock screen on USB insertion
                    self.lock_screen_callback()
            except Exception:
                # Ignore timeout errors and continue looping
                pass

    def stop(self):
        self.running = False
        # Clean up WMI resources
        pythoncom.CoUninitialize()
        self.join()


# =============================================================================
# Section 6: Persistence Helpers
# Simulated functions to add or remove the application from Windows startup.
# In production, you would create or remove a registry entry here.
# =============================================================================
def add_to_startup():
    print("Auto-start persistence enabled (simulate registry entry).")

def remove_from_startup():
    print("Removed auto-start persistence (simulate registry removal).")


# =============================================================================
# Section 7: Main Application Class
# This class sets up the main functionalities: splash screen, system tray, USB
# monitoring, and timed execution if specified.
# =============================================================================
class USBBlockerApp(QtWidgets.QApplication):
    def __init__(self, args, override_code, custom_name, run_time=None):
        super().__init__(args)
        self.override_code = override_code
        self.custom_name = custom_name
        self.run_time = run_time
        self.tray_icon = None
        self.usb_monitor = None
        self.lock_screen_displayed = False

        # Set the application name (affects window titles and metadata)
        self.setApplicationName(self.custom_name)

        # Show the splash screen with a 10-second countdown
        self.splash = SplashScreen(countdown=10)
        self.splash.show()
        # After splash, start the main app functionalities
        QtCore.QTimer.singleShot(10000, self.start_app)
        self.exec_()  # Start the event loop to keep the application running

    def start_app(self):
        self.splash.close()
        # Check if the icon file exists and display a message on the console
        icon_path = resource_path('usb_blocker_icon.png')
        if not os.path.exists(icon_path):
            print(f"Icon file '{icon_path}' not found. Please ensure it exists in the working directory.")
        else:
            print(f"Icon file '{icon_path}' found.")
            # Create and show the system tray icon
            icon = QtGui.QIcon(icon_path)
            self.tray_icon = SystemTrayIcon(icon, stop_callback=self.stop_app)
            self.tray_icon.show()

        # Start the USB monitor thread to listen for USB insertion events
        self.usb_monitor = USBMonitor(lock_screen_callback=self.show_lock_screen)
        self.usb_monitor.start()

        # If a run time is specified, schedule the app to stop after that duration
        print(f"Application will run for {self.run_time} seconds." if self.run_time else "No runtime specified.")

        # Schedule the app to stop after the specified run time
        if self.run_time:
            QtCore.QTimer.singleShot(self.run_time * 1000, self.stop_app)
        else:
            print("No runtime specified. Running indefinitely...")

        # Periodically check for the stop flag file (set via command line or tray)
        self.check_stop_flag()

    def check_stop_flag(self):
        if os.path.exists(stop_flag_file):
            self.stop_app()
        else:
            QtCore.QTimer.singleShot(1000, self.check_stop_flag)

    def show_lock_screen(self):
        if not self.lock_screen_displayed:
            self.lock_screen_displayed = True
            self.lock_screen = LockScreen(self.override_code)
            self.lock_screen.show()
            # When the lock screen is closed, reset the flag so it can be shown again
            self.lock_screen.destroyed.connect(lambda: setattr(self, 'lock_screen_displayed', False))

    def stop_app(self):
        # Stop the USB monitor thread
        if self.usb_monitor:
            self.usb_monitor.stop()
        # Remove auto-start persistence
        remove_from_startup()
        # Show a confirmation screen
        self.confirmation = ConfirmationScreen("Application is stopping...")
        self.confirmation.show()
        # Release the instance lock if it exists
        if hasattr(self, "instance_lock") and self.instance_lock:
            release_instance_lock(self.instance_lock)
            self.instance_lock = None
        # Exit the application after a short delay (3 seconds)
        QtCore.QTimer.singleShot(3000, self.quit)


# =============================================================================
# Section 8: Command-Line Interface & Main Function
# Parses command-line arguments and starts or stops the app accordingly.
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Windows USB Blocker App")
    parser.add_argument("action", choices=["start", "stop"], help="Start or stop the application")
    parser.add_argument("--override", required=True, help="Override code for stopping/unlocking")
    parser.add_argument("--run_time", type=int, help="Time in seconds to run before auto-stop")
    parser.add_argument("--name", default="Process 101", help="Custom name for the app (as seen in Task Manager)")
    args = parser.parse_args()
    
    # Alert the user about the action being taken using pyQt5 message box
    alert = QtWidgets.QMessageBox()
    alert.setText(f"Action: {args.action}\nOverride Code: {args.override}\nCustom Name: {args.name}")
    alert.setWindowTitle("USB Blocker")
    alert.setIcon(QtWidgets.QMessageBox.Information)
    alert.setStandardButtons(QtWidgets.QMessageBox.Ok)
    alert.exec_()
    
    if args.action == "start":
        # Try to acquire a single-instance lock
        lock_file = acquire_instance_lock()
        if not lock_file:
            print("Another instance is already running. Exiting.")
            sys.exit(1)
        # Simulate adding to startup for persistence
        add_to_startup()
        # Start the Qt application and store the instance lock
        app = USBBlockerApp(sys.argv, override_code=args.override, custom_name=args.name, run_time=args.run_time)
        app.instance_lock = lock_file
        
        sys.exit(app.exec_())

    elif args.action == "stop":
        # Write the stop flag to signal a running instance to shut down
        with open(stop_flag_file, 'w') as f:
            f.write("stop")
        print("Stop command issued. Use override code if required to unlock.")

if __name__ == '__main__':
    main()
