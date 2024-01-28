
import logging
import time
import queue 
import sys
import tkinter as tk
from tkinter import ttk
from queue import Queue
from threading import Thread
from tkinter import filedialog, messagebox
from gui_log_handler import GUIConsoleLogHandler
from main import main as  main_run_script


class ATMLogGrapperApp:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("ATM LOG Collector")
        self.root.geometry(f"{width}x{height}")
        self.root.iconbitmap('coop.ico')
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Intercept the close button event
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
        #time  
        self.start_time = 0
        self.update_interval = 100 
        self.last_execution_time = 0  

        
       
        self.create_gui_elements()
    
    def on_closing(self):
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
         
                sys.exit()
   
    def run_script(self):
         # Reset the start time
        self.disable_buttons()
        self.start_time = time.time()
        self.progress_bar.start()
            # Disable the main exit window button during script execution
        self.disable_main_exit_button()
         # Set the script running flag
        self.script_running = True

        atm_config_path = self.atmconfig_path_entry.get()
        shared_folder_name = self.shared_folder_entry.get()
        logs_path = self.logs_path_entry.get()
        
        # Start the timer for execution time
        self.update_execution_time()

        # Start the script execution in a separate thread
        self.script_execution_thread = Thread(target=self.execute_script, args=(atm_config_path, shared_folder_name, logs_path))
        self.script_execution_thread.start()

        # Update the start time label
        self.start_time_label.config(text=f"Start Time: {time.strftime('%H:%M:%S', time.localtime(self.start_time))}")
    
    def create_gui_elements(self):
                # Logo
                self.logo_image = tk.PhotoImage(file="logo.png")
                self.logo_label = ttk.Label(self.main_frame, image=self.logo_image)
                self.logo_label.grid(row=0, column=0, columnspan=1, pady=20)

                # Left side
                left_frame = ttk.Frame(self.main_frame)
                left_frame.grid(row=1, column=0, padx=10, sticky=tk.W)

                ttk.Label(left_frame, text="config.json path:").grid(row=0, column=0, sticky=tk.W, pady=(10, 5))
                self.atmconfig_path_entry = ttk.Entry(left_frame)
                self.atmconfig_path_entry.grid(row=0, column=1, sticky=tk.W, pady=(10, 5))
                self.atmconfig_path_entry.insert(0, ".\\atm_config.json")
                # Buttons for choosing paths
                ttk.Button(left_frame, text="Choose File", command=self.choose_atm_config).grid(row=0, column=2, padx=(10, 0))
                ttk.Button(left_frame, text="Choose path", command=self.choose_logs_path).grid(row=2, column=2, padx=(10, 0))

                ttk.Label(left_frame, text="Shared folder name of all ATMs:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
                self.shared_folder_entry = ttk.Entry(left_frame)
                self.shared_folder_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 5))
                self.shared_folder_entry.insert(0, "EJLogs")

                ttk.Label(left_frame, text="Path to cop ATM Logs:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
                self.logs_path_entry = ttk.Entry(left_frame)
                self.logs_path_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 5))
                self.logs_path_entry.insert(0, "C:\\ATMLogs")

                self.run_button = ttk.Button(left_frame, text="Run Script", command=self.run_script)
                self.run_button.grid(row=3, column=0, columnspan=2, pady=10)

                # Right side
                right_frame = ttk.Frame(self.main_frame)
                right_frame.grid(row=1, column=1, padx=10, sticky=tk.W)
                # Create the title label for the console log
                self.title_label = ttk.Label(right_frame, text="Status Log", font=("Helvetica", 12, "bold"))
                self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))
               # Create the console log text widget with horizontal expansion and text wrapping
                self.console_log_text = tk.Text(right_frame, height=15, width=70, wrap=tk.WORD)
                self.console_log_text.grid(row=1, column=0, padx=10, pady=5, sticky=tk.NSEW)

                # Configure grid column and row weights to allow horizontal and vertical expansion
                right_frame.grid_columnconfigure(0, weight=1)
                right_frame.grid_rowconfigure(1, weight=1)
                # Progress bar
                self.progress_bar = ttk.Progressbar(right_frame, mode="indeterminate")
                self.progress_bar.grid(row=2, column=0, columnspan=2, pady=5)

                # Execution time label
                self.execution_time_label = ttk.Label(right_frame, text="Execution Time: 0 seconds")
                self.execution_time_label.grid(row=3, column=0, columnspan=2, pady=5)

                # Start time label
                self.start_time_label = ttk.Label(right_frame, text="Start Time: -")
                self.start_time_label.grid(row=4, column=0, columnspan=2, pady=5)
                
                
                footer_text = "Made With  ❤️ \n COOP Bank of Oromia \n Payment Switch Acquiring Team \n 2024"
                footer_label = ttk.Label(self.main_frame, text=footer_text, anchor="center", justify="center")
                footer_label.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="nsew")

                # Configure the grid so that the label spans the whole width
                self.main_frame.grid_columnconfigure(0, weight=1)
                self.main_frame.grid_rowconfigure(2, weight=1)
                # Configure grid column and row weights to allow horizontal and vertical expansion
                right_frame.grid_columnconfigure(0, weight=1)
                right_frame.grid_rowconfigure(1, weight=1)

    def choose_atm_config(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.atmconfig_path_entry.delete(0, tk.END)
            self.atmconfig_path_entry.insert(0, path)

    def choose_logs_path(self):
        path = filedialog.askdirectory()
        if path:
            self.logs_path_entry.delete(0, tk.END)
            self.logs_path_entry.insert(0, path)
   
    def execute_script(self, atm_config_path, shared_folder_name, logs_path):
        try:
            # Call the backend function with the provided parameters
           main_run_script(atm_config_path, shared_folder_name, logs_path)
        except Exception as e:
            logging.exception("An error occurred while running the script")
        finally:
            # Once the script execution is complete, stop the execution time update
            self.stop_execution_time_update()
            self.progress_bar.stop()
            self.enable_buttons()
            self.enable_main_exit_button()  # Re-enable the main exit button
            self.script_running = False 

    def update_console_log(self):
        while True:
            try:
                log_message = self.log_queue.get(timeout=0.1)
                self.console_log_text.insert(tk.END, log_message + '\n')
                self.console_log_text.see(tk.END)
            except queue.Empty:
                pass
  
    def update_execution_time(self):
            # Update the execution time label
        if self.start_time != 0:
            current_time = time.time()
            execution_time = current_time - self.start_time
            self.execution_time_label.config(text=f"Execution Time: {execution_time:.2f} seconds")

            # Schedule the next update
            self.root.after(100, self.update_execution_time)

    def stop_execution_time_update(self):
    # Stop the execution time update
        if self.start_time != 0:
            # Store the last counted time
            self.last_execution_time = time.time() - self.start_time
        self.start_time = 0
        # Set the execution time label to the last counted time
        self.execution_time_label.config(text=f"Execution Time: {self.last_execution_time:.2f} seconds")

    def disable_buttons(self):
            self.run_button.config(state="disabled")
           
    def enable_buttons(self):
            self.run_button.config(state="normal")
   
    def disable_main_exit_button(self):
        self.main_exit_button_enabled = False
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable closing via the main exit button

    def enable_main_exit_button(self):
        self.main_exit_button_enabled = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Re-enable closing via the main exit button


if __name__ == "__main__":
    custom_width = 1080
    custom_height = 640
    root = tk.Tk()
    app = ATMLogGrapperApp(root, custom_width, custom_height)
    
    root.mainloop()
    