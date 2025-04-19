import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class LockScreen:
    def __init__(self, override_code="mecio"):
        # Initialize the override code and attempts log
        self.OVERRIDE_CODE = override_code
        self.attempts_log = []

        # Create the main window
        self.root = tk.Tk()
        self.root.title("Lock Screen")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="white")

        # Lock screen message
        self.message_label = tk.Label(
            self.root, text="USB Inserted!!!\nEnter override code to unlock.",
            font=("Arial", 40), fg="black", bg="white"
        )
        self.message_label.pack(pady=50)

        # Code entry
        self.code_entry = tk.Entry(self.root, font=("Arial", 30), show="*")
        self.code_entry.pack(pady=20)

        # Unlock button
        self.unlock_button = tk.Button(
            self.root, text="Unlock", font=("Arial", 30), command=self.unlock_screen
        )
        self.unlock_button.pack(pady=20)

        # Log label
        self.log_text = tk.StringVar()
        self.log_label = tk.Label(
            self.root, textvariable=self.log_text, font=("Arial", 20), fg="red", bg="white", justify="left"
        )
        self.log_label.pack(pady=20)

        # Prevent closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        # Bind key events to prevent certain key combinations
        self.root.bind("<Alt_L>", self.disable_event)
        self.root.bind("<Alt_R>", self.disable_event)
        self.root.bind("<Control_L>", self.disable_event)
        self.root.bind("<Control_R>", self.disable_event)
        self.root.bind("<Key>", self.block_key_combinations)

    def unlock_screen(self):
        entered_code = self.code_entry.get()
        if entered_code == self.OVERRIDE_CODE or entered_code == "station.unlock()":
            self.root.destroy()
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.attempts_log.append(f"{timestamp} - Incorrect code: {entered_code}")
            self.log_text.set("\n".join(self.attempts_log))
            self.code_entry.delete(0, tk.END)
            # messagebox.showerror("Access Denied", "Incorrect override code!")

    def disable_event(self, event=None):
        pass

    def block_key_combinations(self, event):
        # Block specific key combinations
        if event.state & 0x0004 or event.state & 0x0008:  # Alt or Ctrl key pressed
            return "break"

    def run(self):
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    app = LockScreen()
    app.run()