from subprocess import Popen, PIPE
from lock_screen import LockScreen #typ: ignore[import]

class AsynchronousRunner:
    def __init__(self):
        self.monitor_process = None
        self.lock_screen = LockScreen(override_code="abc")

    def run_usb_watcher(self):
        try:
            # Start the USB watcher script asynchronously
            splash_screen_process = Popen(["python", "splash_screen.py"], stdout=PIPE, stderr=PIPE)
            print(f"Splash screen started with PID: {splash_screen_process.pid}")
            
            self.monitor_process = Popen(["python", "usb_Watcher.py"], stdout=PIPE, stderr=PIPE)
            print(f"USB watcher started with PID: {self.monitor_process.pid}")
            
            while self.monitor_process:
                monitor_process_feedback = self.monitor_process.stdout.readline()
                
                if "inserted" in monitor_process_feedback.decode('utf-8').lower():
                    self.lock_screen.run()
                
        except KeyboardInterrupt as e:
            print(f"User interrupted the process: {e}")
            if self.monitor_process:
                self.monitor_process.terminate()
                print(f"Process with PID {self.monitor_process.pid} terminated.")
    
    def main(self):
        self.run_usb_watcher()
        
if __name__ == "__main__":
    runner = AsynchronousRunner()
    runner.main()
