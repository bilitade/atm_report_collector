# Import necessary modules
import tkinter as tk
from tkinter import ttk
from queue import Queue
from threading import Thread
import logging
from gui_log_handler import GUIConsoleLogHandler
from main import main as run_script
import queue 

class ATMLogGrapperApp:
    def __init__(self, root, width, height):
        # Initialize GUI elements
        self.root = root
        self.root.title("ATM LOGO Grapper")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)

        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Initialize logging queue
        self.log_queue = Queue()

        # Create logging handler
        gui_log_handler = GUIConsoleLogHandler(self.log_queue)
        gui_log_handler.setLevel(logging.DEBUG)

        # Create logging formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%I-%M-%S%p %Y-%m-%d')
        gui_log_handler.setFormatter(formatter)

        # Add logging handler to root logger
        logging.getLogger().addHandler(gui_log_handler)

        # Start thread to update console log
        self.update_console_log_thread = Thread(target=self.update_console_log)
        self.update_console_log_thread.daemon = True
        self.update_console_log_thread.start()

        # Create GUI elements
        self.create_gui_elements()

     

    def run_script(self):
        # Get paths and configurations from GUI elements
        atm_config_path = self.atmconfig_path_entry.get()
        shared_folder_name = self.shared_folder_entry.get()
        logs_path = self.logs_path_entry.get()

        # Start the script execution in a separate thread
        self.script_execution_thread = Thread(target=self.execute_script, args=(atm_config_path, shared_folder_name, logs_path))
        self.script_execution_thread.start()
    def create_gui_elements(self):
        # Logo
        self.logo_image = tk.PhotoImage(file="logo.png")
        self.logo_label = ttk.Label(self.main_frame, image=self.logo_image)
        self.logo_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Left side
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=1, column=0, padx=10, sticky=tk.W)

        ttk.Label(left_frame, text="ATMConfig.json file path:").grid(row=0, column=0, sticky=tk.W, pady=(10, 5))
        self.atmconfig_path_entry = ttk.Entry(left_frame)
        self.atmconfig_path_entry.grid(row=0, column=1, sticky=tk.W, pady=(10, 5))
        self.atmconfig_path_entry.insert(0, ".\\atm_config.json")

        ttk.Label(left_frame, text="Shared folder name of all ATMs:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.shared_folder_entry = ttk.Entry(left_frame)
        self.shared_folder_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 5))
        self.shared_folder_entry.insert(0, "EJLogs")

        ttk.Label(left_frame, text="Path to copy logs:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.logs_path_entry = ttk.Entry(left_frame)
        self.logs_path_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 5))
        self.logs_path_entry.insert(0, "C:\\ATMLogs")

        self.run_button = ttk.Button(left_frame, text="Run Script", command=self.run_script)
        self.run_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Right side
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=1, column=1, padx=10, sticky=tk.W)

        # Scrollbars for console log text
        scrollbar_y = ttk.Scrollbar(right_frame, orient=tk.VERTICAL)
        scrollbar_y.grid(row=0, column=1, sticky=tk.NS)

        scrollbar_x = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=tk.EW)

        self.console_log_text = tk.Text(right_frame, height=20, width=80, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)  
        self.console_log_text.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)

        scrollbar_y.config(command=self.console_log_text.yview)
        scrollbar_x.config(command=self.console_log_text.xview)

        ttk.Label(right_frame, text="ATMs connected:").grid(row=2, column=0, sticky=tk.W)
        self.atms_connected_label = ttk.Label(right_frame, text="0")
        self.atms_connected_label.grid(row=2, column=1, sticky=tk.W, pady=5)

        self.progress_bar = ttk.Progressbar(right_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=2, pady=5)

        self.cancel_button = ttk.Button(right_frame, text="Cancel", command=self.cancel_operation)
        self.cancel_button.grid(row=4, column=0, columnspan=2, pady=10)
    def execute_script(self, atm_config_path, shared_folder_name, logs_path):
        try:
            # Call the backend function with the provided parameters
            run_script(atm_config_path, shared_folder_name, logs_path)
        except Exception as e:
            logging.exception("An error occurred while running the script")

    def cancel_operation(self):
        # Stop the script execution thread if it is running
        if hasattr(self, 'script_execution_thread') and self.script_execution_thread.is_alive():
            logging.warning("Cancelling operation...")
            # Add your cancellation logic here
            # For example, you can set a flag to indicate cancellation
        else:
            logging.info("No operation to cancel.")

    def update_console_log(self):
        while True:
            try:
                log_message = self.log_queue.get(timeout=0.1)  # Check for new log messages every 0.1 seconds
                self.console_log_text.insert(tk.END, log_message + '\n')
                self.console_log_text.see(tk.END)  # Auto-scroll to the bottom of the text widget
            except queue.Empty:  # Use queue.Empty to handle the exception
                pass
if __name__ == "__main__":
    # Set custom resolution
    custom_width = 1200
    custom_height = 800

    root = tk.Tk()
    app = ATMLogGrapperApp(root, custom_width, custom_height)
    root.mainloop()
