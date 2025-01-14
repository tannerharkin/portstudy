"""Path utilities for PortStudy application."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import platform
from pathlib import Path

def get_app_data_dir() -> Path:
    """Get the appropriate application data directory for the current platform."""
    system = platform.system().lower()
    
    if system == 'windows':
        base_dir = os.environ.get('APPDATA')
        if not base_dir:
            base_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming')
        return Path(base_dir) / 'PortStudy'
    
    elif system == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'PortStudy'
    
    else:  # Linux and other Unix-like systems
        return Path.home() / '.port_study'

def get_save_file_path() -> Path:
    """Get the path to the save file."""
    return get_app_data_dir() / 'game_state.json'

def get_backup_save_file_path() -> Path:
    """Get the path to the backup save file."""
    return get_app_data_dir() / 'game_state.backup.json'

def get_data_file_path() -> Path:
    """Get the path to the ports data file."""
    return Path(__file__).parent.parent / 'data' / 'ports.json'

def ensure_app_dirs_exist() -> None:
    """Ensure all necessary application directories exist."""
    app_dir = get_app_data_dir()
    app_dir.mkdir(parents=True, exist_ok=True)