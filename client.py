import argparse
import subprocess
import sys
import os
import time
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton # type: ignore
from PyQt5.QtWidgets import QApplication, QMessageBox  # type: ignore

# Global variables to store the running process and its PID.
running_process = None
running_process_id = None

def write_to_process(process, command):
    """
    Write a command to the process's standard input.
    """
    if process is not None:
        try:
            process.stdin.write(command + "\n")
            process.stdin.flush()
        except Exception as e:
            print(f"Error writing to process: {e}")

def read_from_process(process):
    """
    Read one line of output from the process's standard output.
    """
    if process is not None:
        try:
            return process.stdout.readline().strip()
        except Exception as e:
            print(f"Error reading from process: {e}")
            return None
    return None

def send_to_process(process, command):
    """
    Write the command to the process and return its immediate response.
    """
    if process is not None and command is not None:
        write_to_process(process, command)
        return read_from_process(process)
    elif command is None:
        return "Cannot send empty command to process"
    else:
        return "USB Monitor is not running"

def evaluate_if_blocker_is_running():
    """
    Check whether the blocker process is running.
    Returns True if running, False otherwise.
    """
    global running_process, running_process_id
    if running_process_id is not None and running_process is not None:
        # running_process.poll() returns None if still running.
        return running_process.poll() is None
    return False

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_blocker_runtime_path():
    """
    Determine the path to monitor.exe.  
    If the application is bundled (sys.frozen), use sys._MEIPASS; otherwise, use the current directory.
    """
    return resource_path("monitor.exe")

def start_blocker(override_code, run_time=None):
    """
    Starts monitor.exe as a subprocess if it's not already running.
    Constructs the command line and spawns the process.
    """
    global running_process, running_process_id

    if evaluate_if_blocker_is_running():
        QMessageBox.information(None, "Info", "USB Monitor is already running.")
        return

    tool_path = get_blocker_runtime_path()
    print(f"Tool path: {tool_path}")
    # Build the command using Windows’ start /B command (background, without a terminal)
    # and the override code.
    # The command is passed as a list to avoid shell injection issues.
    command = [tool_path, "start", "--override", override_code]
    print(f"Command: {command}")
    if run_time:
        # If run_time is provided, append it to the command.
        command.append("--run_time")
        command.append(str(run_time))

    try:
        # Start the monitor. shell=True is needed to run the "start" command.
        running_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        retry_count = 0
        
        details = f"USB Monitor started successfully with PID {running_process_id}\nRunning process: {running_process}" if running_process else "Failed to start USB Monitor"
        
        while running_process.poll() is None and retry_count < 10:
            # Wait for the process to initialize.
            time.sleep(100)  # Allow time for monitor.exe to initialize.
            
            # Read the output from the process to check if it started successfully.
            output = read_from_process(running_process)
            
            details += "\nWaiting for process to initialize... retry count: {retry_count} \t Output: {output}"
            
            # Check if the process is still running.
            retry_count += 1
            

        dialog = QDialog()
        dialog.setWindowTitle("USB Monitor Status")
        layout = QVBoxLayout()

        label = QLabel("Process Information")
        layout.addWidget(label)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(details)
        layout.addWidget(text_edit)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec_()
        
        if running_process.poll() is not None:
            # Process terminated prematurely – it failed to start.
            QMessageBox.critical(None, "Error", "USB Monitor failed to start.")
            running_process = None
            running_process_id = None
        else:
            running_process_id = running_process.pid
            QMessageBox.information(None, "Info", f"USB Monitor started successfully with PID {running_process_id}")
            
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start monitor: {e}")
        running_process = None
        running_process_id = None

def stop_blocker():
    """
    Stops monitor.exe. If the monitor supports a command interface,
    attempt to send "STOP" via its stdin; otherwise, terminate it.
    """
    global running_process, running_process_id

    if not evaluate_if_blocker_is_running():
        QMessageBox.information(None, "Info", "USB Monitor is not running.")
        return

    try:
        # Option 1: If the monitor.exe is designed to read commands, try sending "STOP"
        response = send_to_process(running_process, "STOP")
        print("USB Monitor responded:", response)
    except Exception as e:
        print("Error sending STOP command:", e)
    finally:
        # Option 2: Terminate the process if it is still alive.
        if running_process.poll() is None:
            running_process.terminate()
            try:
                running_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                running_process.kill()
                running_process.wait()
        running_process = None
        running_process_id = None
        QMessageBox.information(None, "Info", "USB Monitor stopped successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="App Interface for USB Monitor tool")
    parser.add_argument("action", choices=["start", "stop"], help="Action to perform")
    parser.add_argument("--override", required=True, help="Override code for stopping/unlocking")
    parser.add_argument("--run_time", type=int, help="Time in seconds to run the monitor")
    args = parser.parse_args()
    print(f"Client started with Arguments: {args}")
    # Create a QApplication to support message boxes.
    app = QApplication(sys.argv)

    if args.action == "start":
        start_blocker(args.override, args.run_time)
    elif args.action == "stop":
        stop_blocker()

    sys.exit(app.exec_())
