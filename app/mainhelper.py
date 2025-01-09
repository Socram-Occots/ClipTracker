# mainhelper.y
# providing misc functions for main

#imports
import webbrowser
from datetime import date
import os
import json

def seconds_to_hms(seconds) -> tuple[int, int, int]:
    """
    Converts seconds in int or float into a tuple:

    int(hours), int(minutes), int(seconds)
    """
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return int(hours), int(minutes), int(seconds)

def callback(url : str):
   """
   Opens a url using webbrowser.open_new_tab
   """
   webbrowser.open_new_tab(url)

def save_list(directory: str, listy: list, num: int) -> str:
    """
    Saves the a list (in this case markers) using this format: timeline{num}_{date.today()}.txt

    Returns the filename generated from the format 
    """
    filename = f"timeline{num}_{date.today()}.txt"
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w') as f:
        for line in listy:
            f.write(f"{line}\n")

    return filename

def save_settings(timeline_keys : list, marker_keys : list, marker_dir : str, total_timelines : int):
    """
    Saves the timeline and marker keys as lists along with the directory used for saving markers.

    IMPORTANT: the save settings are always saved in the same directory of main.py

    Settings are saved as "cliptrackersettings.json"
    """
    data : dict = {"timeline_key": timeline_keys, "marker_key": marker_keys, 
                   "save_directory" : marker_dir, "total_timelines" : total_timelines}
    with open("cliptrackersettings.json", "w") as outfile:
        json.dump(data, outfile)

def read_settings() -> dict:
    """
    Reads in "cliptrackersettings.json" and returns the resulting dictionary
    """
    with open("cliptrackersettings.json", "r") as infile:
        settings : dict = json.load(infile)
    return settings

def check_settings_exist() -> bool:
    """Checks to see if "cliptrackersettings.json" exists and returns the respecting bool"""
    return os.path.exists("cliptrackersettings.json")