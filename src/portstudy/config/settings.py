"""Configuration information for the PortStudy application."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from typing import Dict, Optional

# Level progression requirements - now includes level 5
LEVEL_REQUIREMENTS: Dict[int, Dict[str, Optional[int]]] = {
    1: {"accuracy": 75, "streak": 15, "window": 45},
    2: {"accuracy": 80, "streak": 20, "window": 90},
    3: {"accuracy": 85, "streak": 30, "window": 90},
    4: {"accuracy": 87, "streak": 35, "window": 90},
    5: {"accuracy": None, "streak": None, "window": None}  # Max level
}

# Question generation settings
QUESTION_CHOICES = 4
REDEMPTION_CHANCE = 0.5  # 50% chance for redemption questions

# Question type weights (higher number = more frequent)
QUESTION_TYPE_WEIGHTS = {
    "standard": 80,  # Regular multiple choice questions
    "port_entry": 20  # Direct port number entry questions
}

# Port difficulty weights (higher number = more frequent)
PORT_DIFFICULTY_WEIGHTS = {
    "beginner": 100,
    "intermediate": 70,
    "advanced": 30
}

# Save data integrity keys (16-bit)
SAVE_INTEGRITY_KEYS = {
    "accuracy": 0x55AA,  # 0101 0101 1010 1010 - alternating pattern
    "streak": 0xAA55     # 1010 1010 0101 0101 - inverse alternating pattern
}

# ASCII Art for the main menu - if you modify the program, please note that here
ASCII_ART = """
    ______          _   _____ _             _       
    | ___ \        | | /  ___| |           | |      
    | |_/ /__  _ __| |_\ `--.| |_ _   _  __| |_   _ 
    |  __/ _ \| '__| __|`--. \ __| | | |/ _` | | | |  PortStudy v2.4
    | | | (_) | |  | |_/\__/ / |_| |_| | (_| | |_| |  A certification/test practice utility
    \_|  \___/|_|   \__\____/ \__|\__,_|\__,_|\__, |  by Tanner Harkin
                \                              __/ |
                 \------------------------(|= |___/   
"""

# Main menu options
MENU_OPTIONS = {
    "1": "Practice Mode",
    "2": "View Statistics",
    "3": "Exit"
}

# Color thresholds for accuracy display
ACCURACY_COLOR_THRESHOLDS = [
    (90, "GREEN"),
    (80, "LIGHTGREEN_EX"),
    (70, "YELLOW"),
    (60, "LIGHTYELLOW_EX"),
    (0, "RED")
]