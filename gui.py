import tkinter as tk
from tkinter import ttk
from queue import Queue
from threading import Thread
import logging
import time
from gui_log_handler import GUIConsoleLogHandler
from main import main as run_script
import queue 

class ATMLogGrapperApp:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("ATM LOGO Grapper")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.log_queue = Queue()
        gui_log_handler = GUIConsoleLogHandler(self.log_queue)
        gui_log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%I-%M-%S%p %Y-%m-%d')
        gui_log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(gui_log_handler)
        self.update_console_log_thread = Thread(target=self.update_console_log)
        self.update_console_log_thread.daemon = True
        self.update_console_log_thread.start()
        self.start_time = 0  # Initialize start_time
        self.create_gui_elements()

    def run_script(self):
        self.start_time = time.time()  # Update start_time
        atm_config_path = self.atmconfig_path_entry.get()
        shared_folder_name = self.shared_folder_entry.get()
        logs_path = self.logs_path_entry.get()
        # Start the script execution in a separate thread
        self.script_execution_thread = Thread(target=self.execute_script, args=(atm_config_path, shared_folder_name, logs_path))
        self.script_execution_thread.start()
        
        # Update the start time label
        self.start_time_label.config(text=f"Start Time: {time.strftime('%H:%M:%S', time.localtime(self.start_time))}")

 

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

                # Create the console log text widget
                self.console_log_text = tk.Text(right_frame, height=20, wrap=tk.NONE)
                self.console_log_text.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)

                # Add a scrollbar for the console log text widget
                console_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.console_log_text.yview)
                console_scrollbar.grid(row=0, column=1, sticky=tk.NS)
                self.console_log_text.config(yscrollcommand=console_scrollbar.set)

                # Execution time label
                self.execution_time_label = ttk.Label(right_frame, text="Execution Time: 0 seconds")
                self.execution_time_label.grid(row=1, column=0, columnspan=2, pady=5)

                # Start time label
                self.start_time_label = ttk.Label(right_frame, text="Start Time: -")
                self.start_time_label.grid(row=2, column=0, columnspan=2, pady=5)

     
    def execute_script(self, atm_config_path, shared_folder_name, logs_path):
        try:
            # Call the backend function with the provided parameters
            run_script(atm_config_path, shared_folder_name, logs_path)
        except Exception as e:
            logging.exception("An error occurred while running the script")
        finally:
            # Record the end time
            end_time = time.time()

            # Calculate the execution time
            execution_time = end_time - self.start_time

            # Update the execution time label on the GUI
            self.execution_time_label.config(text=f"Execution Time: {execution_time:.2f} seconds")

    def update_console_log(self):
        while True:
            try:
                log_message = self.log_queue.get(timeout=0.1)
                self.console_log_text.insert(tk.END, log_message + '\n')
                self.console_log_text.see(tk.END)
            except queue.Empty:
                pass

if __name__ == "__main__":
    custom_width = 1000
    custom_height = 600
    root = tk.Tk()
    app = ATMLogGrapperApp(root, custom_width, custom_height)
    root.mainloop()
