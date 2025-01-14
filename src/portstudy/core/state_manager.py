"""Manages saving and loading of game states."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import sys
import traceback
import base64
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
from colorama import Fore, Style

from ..utils.paths import get_save_file_path, get_backup_save_file_path
from .game_state import GameState
from ..__init__ import __version__

class StateManager:
    """Handles saving and loading of game states with backup functionality."""
    
    def __init__(self) -> None:
        """Initialize the state manager with appropriate file paths."""
        self.state_file = get_save_file_path()
        self.backup_file = get_backup_save_file_path()
    
    def _generate_bug_report(self, error: Exception, traceback_str: str, save_data: Optional[str] = None) -> str:
        """
        Generate a formatted bug report with error details and save data.
        
        Args:
            error: The exception that triggered the bug report
            traceback_str: The formatted traceback string
            save_data: Optional raw save file content
            
        Returns:
            Formatted bug report string
        """
        timestamp = datetime.now().isoformat()
        
        report = [
            "#### SAVE BUGCHECK STATE DUMP ####",
            f"{timestamp} - {str(error)}",
            "",
            f"VERSION: {__version__}",
            "",
            "STACK TRACE:",
            traceback_str,
        ]
        
        if save_data:
            try:
                encoded_save = base64.b64encode(save_data.encode()).decode()
                report.extend([
                    "",
                    "CURRENT STATE:",
                    encoded_save
                ])
            except Exception as e:
                report.extend([
                    "",
                    "Failed to encode save data:",
                    str(e)
                ])
        
        report.append("##################################")
        return "\n".join(report)
    
    def save_state(self, game_state: GameState) -> bool:
        """
        Save current state with backup.
        
        Args:
            game_state: The current game state to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        state_data = game_state.to_dict()
        
        try:
            # If current state file exists, move it to backup
            if self.state_file.exists():
                self.state_file.replace(self.backup_file)
            
            # Write new state
            with self.state_file.open('w') as f:
                json.dump(state_data, f)
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error saving state: {e}{Style.RESET_ALL}")
            return False
    
    def load_state(self, window_sizes: Dict[int, int]) -> GameState:
        """
        Load state, falling back to backup if needed.
        
        Args:
            window_sizes: Dictionary mapping difficulty levels to window sizes
            
        Returns:
            GameState: The loaded game state or a new state if user chooses to continue
            
        Raises:
            SystemExit: If user chooses to quit after load failure
        """
        save_content = None
        last_error = None
        last_traceback = None
        
        # Try primary save first
        state, error, tb = self._try_load_file(self.state_file, window_sizes)
        if error:
            last_error = error
            last_traceback = tb
            save_content = None
            try:
                with self.state_file.open('r') as f:
                    save_content = f.read()
            except:
                pass
            
            print(f"{Fore.YELLOW}Primary save failed, attempting backup...{Style.RESET_ALL}")
            # Try backup
            state, backup_error, backup_tb = self._try_load_file(self.backup_file, window_sizes)
            if backup_error:
                last_error = backup_error
                last_traceback = backup_tb
        
        if state:
            return state
        
        # If we get here, both primary and backup loads failed
        print(f"\n{Fore.RED}Unable to load primary or backup save data.\nYour save file is corrupted, and automatic recovery has failed.{Style.RESET_ALL}")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}WARNING: If you start fresh, ALL SAVE DATA WILL BE {Fore.RED}ERASED{Fore.YELLOW}!\nIf this is not what you want, do not continue and manually repair your save file.\n\nWould you like to start fresh? (y/n): {Style.RESET_ALL}").lower()
            if choice == 'y':
                print(f"\n{Fore.GREEN}Starting new game...{Style.RESET_ALL}")
                return GameState()
            elif choice == 'n':
                if last_error:
                    bug_report = self._generate_bug_report(
                        last_error,
                        last_traceback or "No traceback available",
                        save_content
                    )
                    print(f"\n{Fore.YELLOW}Please include this bug report when reporting the issue:{Style.RESET_ALL}")
                    print(f"\n{bug_report}")
                print(f"\n{Fore.YELLOW}Exiting to prevent save data loss.{Style.RESET_ALL}")
                sys.exit(1)
            else:
                print(f"{Fore.RED}Please enter 'y' or 'n'{Style.RESET_ALL}")
    
    def _try_load_file(self, file_path: Path, window_sizes: Dict[int, int]) -> Tuple[Optional[GameState], Optional[Exception], Optional[str]]:
        """
        Attempt to load state from a specific file.
        
        Returns:
            Tuple containing:
            - GameState if successful, None if failed
            - Exception if one occurred, None if successful
            - Traceback string if exception occurred, None if successful
        """
        if not file_path.exists():
            return None, None, None
            
        try:
            with file_path.open('r') as f:
                save_content = f.read()
                data = json.loads(save_content)
                return GameState.from_dict(data, window_sizes), None, None
        except Exception as e:
            return None, e, traceback.format_exc()
