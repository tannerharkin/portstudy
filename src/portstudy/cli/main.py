"""Main entry point for the PortStudy application."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import sys
from colorama import Fore, Style

from ..core.state_manager import StateManager
from ..core.question_generator import QuestionGenerator
from ..ui.menu import MenuSystem
from ..utils.paths import get_data_file_path, ensure_app_dirs_exist

def load_port_data() -> dict:
    """Load and validate port configuration data from JSON file.
    
    Attempts to load the port data configuration file and validates its structure.
    Handles common failure cases with user-friendly error messages.
    
    Returns:
        dict: Structured port information including names, codes, and metadata
    
    Raises:
        SystemExit: If the data file is missing or contains invalid JSON
    """
    data_file = get_data_file_path()
    try:
        with data_file.open('r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: ports.json not found. Please ensure the data file exists at {data_file}{Style.RESET_ALL}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: ports.json is corrupted or invalid.{Style.RESET_ALL}")
        sys.exit(1)

def main() -> None:
    """Initialize and launch the PortStudy application.
    
    Performs application setup in the following order:
        1. Ensures required directories exist
        2. Loads port configuration data
        3. Initializes core components (state, question generator)
        4. Launches the menu-driven UI
    
    Raises:
        SystemExit: On unexpected errors, with error details printed to stdout
    """
    try:
        # Ensure application directories exist
        ensure_app_dirs_exist()
        
        # Load port data
        port_info = load_port_data()
        
        # Initialize components
        state_manager = StateManager()
        question_gen = QuestionGenerator(port_info)
        
        # Create and run menu system
        menu = MenuSystem(port_info, state_manager, question_gen)
        menu.main_menu()
        
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
