# main.py
# this file is tasked with providing a simple way to 
# to keep track of certain moments in a continuous timeline

#imports
import time
import tkinter as tk
import keyboard
from threading import Thread
from mainhelper import seconds_to_hms, callback, save_list, save_settings, read_settings, check_settings_exist
from tkinter import filedialog

# The ClipTracker class, handles each operation of the Clip Tracker application
class ClipTracker:
    # Contructor
    def __init__(self, root : tk.Tk):
        """
        Root: tkinter class object

        Example:

        root = tk.Tk()

        app = ClipTracker(root)

        root.mainloop()
        """

        # Initializing state variables
        self.root : tk.Tk = root
        self.default_bind_response : str = ""
        self.save_dir : str = ""
        self.saved_timeline_count : int = 0
        self.timeline_active : bool = False
        self.start_time : int = 0
        self.markers : list[str] = []
        self.current_keys = dict() 
        self.binding_timeline : bool = False
        self.binding_marker : bool = False
        self.website : str = "http://www.tutorialspoint.com"
        # Initial key bindings set to empty/None
        self.timeline_key : list[str] = ["None"]
        self.marker_key : list[str] = ["None"]
        # Title variable
        self.title_var : str = "Clip Tracker 1.0"

        # Title
        self.root.title(self.title_var)
        self.app_title = tk.Label(root, text=self.title_var, font=("Arial", 18))
        self.app_title.pack(pady=10)

        # Instruction label
        self.instruct = tk.Label(root, text="Instructions", fg="blue", cursor="hand2", font=("Arial", 12))
        self.instruct.pack(pady=5)
        self.instruct.bind("<Button-1>", lambda e: callback(self.website))

        # Rebinding key status label
        self.status_label = tk.Label(root, text=self.default_bind_response, font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Formatting app layout
        timeline_column = tk.Frame(self.root)
        button_column = tk.Frame(self.root)
        timeline_column.pack(side="left", fill="both", expand=True)
        button_column.pack(side="left", fill="both", expand=True)

        # Formatting rebinding button layouts
        rebind_timeline_column = tk.Frame(button_column)
        rebind_marker_column = tk.Frame(button_column)


        # Marker display area
        self.marker_display = tk.Text(timeline_column, height=20, width=50, state="disabled")
        self.marker_display.pack(pady=10, padx=(10,10))

        # Key button and labels
        self.timeline_label = tk.Label(button_column, text="Timeline Key: None", font=("Arial", 12))
        self.timeline_label.pack()
        self.marker_label = tk.Label(button_column, text="Marker Key: None", font=("Arial", 12))
        self.marker_label.pack()

        # Rebind timeline key button
        rebind_timeline_column.pack()
        self.rebind_timeline_button = tk.Button(rebind_timeline_column, text="Rebind Timeline Key", command=self.rebind_timeline_key)
        self.rebind_timeline_button.pack(pady=5, side="left", padx=(0,10))

        # Wipe timeline key button
        self.wipe_timeline_rebind = tk.Button(rebind_timeline_column, text="Clear Timeline Key", command=self.clear_timeline_keybind)
        self.wipe_timeline_rebind.pack(pady=5, side="left")

        # Rebind marker key button
        rebind_marker_column.pack()
        self.rebind_marker_button = tk.Button(rebind_marker_column, text="Rebind Marker Key", command=self.rebind_marker_key)
        self.rebind_marker_button.pack(pady=5, side="left", padx=(0,10))

        # Wipe marker key button
        self.wipe_timeline_rebind = tk.Button(rebind_marker_column, text="Clear Marker Key", command=self.clear_marker_keybind)    
        self.wipe_timeline_rebind.pack(pady=5, side="left")

        # Manual Timeline and Marker buttons
        self.marker_button = tk.Button(button_column, text="Start/End Timeline", command=self.toggle_timeline)
        self.marker_button.pack(pady=5)
        self.timeline_button = tk.Button(button_column, text="Place Marker", command=self.record_marker)
        self.timeline_button.pack(pady=5)

        # Choose directory for saving markers button
        self.dir_pref = tk.Button(button_column, text=f"Choose directory\nto save timelines", command=self.save_dir_pref)
        self.dir_pref.pack(pady=5)

        # Save the current timeline of markers button
        self.save_timeline = tk.Button(button_column, text="Save Timeline", command=self.save_timeline_wrap, state="disabled")
        self.save_timeline.pack(pady=5)

        # Label to provide a response after using the directory and save buttons
        self.dir_feedback = tk.Label(button_column, text="Directory: default", font=("Arial", 12), wraplength=200)
        self.dir_feedback.pack(pady=5)

        # Read settings
        self.read_settings_wrap()

        # Start a thread for listening to global key events
        self.listener_thread = Thread(target=self.start_key_listener, daemon=True)
        self.listener_thread.start()

        # Debuging content. Not to be used in production
        # self.debug_current_text = tk.Label(root, text="debug_current_text", font=("Arial", 12))
        # self.debug_timeline_text = tk.Label(root, text="debug_timeline_text", font=("Arial", 12))
        # self.debug_binding_timeline = tk.Label(root, text="debug_binding_timeline", font=("Arial", 12))
        # self.debug_current_text.pack(pady=5)
        # self.debug_timeline_text.pack(pady=5)
        # self.debug_binding_timeline.pack(pady=5)

    #Methods
    def toggle_timeline(self):
        """Start or stop the timeline."""
        if not self.timeline_active:
            self.timeline_active = True
            self.start_time = time.time()
            self.markers.clear()
            self.marker_display.config(state='normal')
            self.marker_display.delete(1.0, tk.END)
            self.marker_display.config(state='disabled')
            self.update_marker_display("Timeline started.\n")
            self.save_timeline.config(state="disabled")
        else:
            self.timeline_active = False
            self.update_marker_display("Timeline stopped.\n")
            self.save_timeline.config(state="normal")

    def record_marker(self):
        """Record a marker if the timeline is active."""
        if self.timeline_active:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            hours, minutes, seconds = seconds_to_hms(elapsed_time)
            hour_min_sec_string = f"Hour: {hours}, Min: {minutes}, Sec: {seconds}"
            self.markers.append(hour_min_sec_string)
            self.update_marker_display(f"Marker at {hour_min_sec_string}.\n")

    def update_marker_display(self, text : str):
        """Update the marker display with new text."""
        self.marker_display.config(state='normal')
        self.marker_display.insert('end', text)
        self.marker_display.see('end')
        self.marker_display.config(state='disabled')

    def rebind_timeline_key(self):
        """Enable rebinding of the timeline key."""
        if not self.binding_marker:
            self.binding_timeline = True
            self.status_label.config(text="Press any key combination to set as the new timeline key...")

    def set_timeline_key(self, keys : list[str]):
        """Set the new timeline key and save it to the settings json."""
        self.binding_timeline = False
        self.timeline_key = keys
        self.save_settings_default()
        self.timeline_label.config(text=f"Timeline Key: {"+".join(keys)}")
        self.status_label.config(text=self.default_bind_response)

    def rebind_marker_key(self):
        """Enable rebinding of the marker key."""
        if not self.binding_timeline:
            self.binding_marker = True
            self.status_label.config(text="Press any key combination to set as the new marker key...")

    def set_marker_key(self, keys : list[str]):
        """Set the new marker key and save it to the settings json."""
        self.binding_marker = False
        self.marker_key = keys
        self.save_settings_default()
        self.marker_label.config(text=f"Marker Key: {"+".join(keys)}")
        self.status_label.config(text=self.default_bind_response)

    def clear_current_keys(self, event):
        """Clear the current key set after a key is released."""
        self.current_keys.clear()

    def start_key_listener(self):
        """
        Begins the thread responible for reading keyboard inputs.
        Starts key_listener and blocks execution with no stop
        """
        keyboard.hook(self.key_listener)
        keyboard.wait()
    
    def key_listener(self, event):
        """
        Reads the inputs from the keyboard. If the key is pressed DOWN, it keeps the key name
        in self.current_keys and also checks to see if it triggers toggle_timeline or record_marker.
        If the key is released (considered UP) then it checks if the app is recording for the timeline
        or marker key. If so, it takes the current keys pressed and triggers set_timeline_key or set_marker_key.
        Regardless, the key in question is deleted from self.current_keys. Note: keys are converted into uppercase.
        """

        key : str
        try:
            key = event.name.upper()
        except:
            key = event.name

        try:
            if event.event_type == keyboard.KEY_DOWN:
                self.current_keys[key] = None
                cur_key_length : int = len(self.current_keys)
                key_keys : list[str] = list(self.current_keys.keys())
                if key_keys == self.timeline_key and cur_key_length > 0:
                    self.toggle_timeline()
                elif key_keys == self.marker_key and cur_key_length > 0:
                    self.record_marker()

            elif event.event_type == keyboard.KEY_UP:
                key_keys : list[str] = list(self.current_keys.keys())
                if self.binding_timeline:
                    self.set_timeline_key(key_keys.copy())
                elif self.binding_marker:
                    self.set_marker_key(key_keys.copy())
                del self.current_keys[key]
        except:
            pass

            # Debuging content. Not to be used in production
            # self.debug_current_text.config(text=f"{self.current_keys}")
            # self.debug_timeline_text.config(text=f"{self.timeline_key}")
            # self.debug_binding_timeline.config(text=f"{self.binding_timeline}")

            # Debuging content. Not to be used in production
            # self.debug_current_text.config(text=f"{self.current_keys}")
            # self.debug_timeline_text.config(text=f"{self.timeline_key}")
            # self.debug_binding_timeline.config(text=f"{self.binding_timeline}")

    def save_dir_pref(self):
        """
        Activated when user changes their marker save directory
        
        Leads to save_dir_pref_helper
        """
        directory : str = filedialog.askdirectory(mustexist=True)
        if directory:
            self.save_dir_pref_helper(directory)

    def save_dir_pref_helper(self, directory : str):
        """
        Activated from save_dir_pref or read_settings_wrap

        If the direcory is empty, dir_feedback is set to default
        Otherwise, it is set to show the directory.

        Then calls mainhelper.save_settings to save the directory
        """
        self.save_dir = directory
        self.save_settings_default()
        if directory == "":
            self.dir_feedback.config(text=f"Directory: default")
        else:
            self.dir_feedback.config(text=f"Directory: {directory}")
    
    def save_timeline_wrap(self):
        """
        Uses mainhelper.save_list wih save save_dir, markers, saved_timeline_count
        to save the markers in a text file in a specified location
        Also sets dir_feedback to reflect this action
        """
        self.saved_timeline_count += 1
        self.save_settings_default()
        filename = save_list(self.save_dir, self.markers, self.saved_timeline_count)
        self.dir_feedback.config(text=f"File {filename} saved at: {self.save_dir}")

    def read_settings_wrap(self):
        """
        First uses mainhelper.check_settings_exist to check if the settings have been saved before.
        
        Uses mainhelper.read_settings to extract the settings json file and uses
        save_dir_pref_helper, set_timeline_key, and set_marker_key to set them.
        Also, sets 

        If there is no settings available mainhelper.save_settings is called with default values.
        """
        if check_settings_exist():
            settings : dict = read_settings()
            self.save_dir_pref_helper(settings["save_directory"])
            self.set_timeline_key(settings["timeline_key"])
            self.set_marker_key(settings["marker_key"])
            self.saved_timeline_count = settings["total_timelines"]
        else:
            self.save_settings_default()
            
    def save_settings_default(self):
        """
        Calls save_settings and uses the typical parameters:

        save_settings(timeline_keys = self.timeline_key, marker_keys = self.marker_key, 
        marker_dir = self.save_dir,total_timelines = self.saved_timeline_count)
        """
        save_settings(timeline_keys = self.timeline_key, marker_keys = self.marker_key, 
            marker_dir = self.save_dir,total_timelines = self.saved_timeline_count)
        
    def clear_timeline_keybind(self):
        """
        Calls set_timeline_key with list[str] = [None] to clear the keybind.
        """
        self.set_timeline_key(keys=["None"])

    def clear_marker_keybind(self):
        """
        Calls set_marker_key with list[str] = [None] to clear the keybind.
        """
        self.set_marker_key(keys=["None"])

# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ClipTracker(root)
    root.mainloop()