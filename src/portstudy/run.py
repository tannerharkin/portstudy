"""Bootstrap for PyInstaller binary to launch program in Windows Terminal."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import subprocess
import platform
import os
import ctypes

def hide_console():
    """Hide the console window on Windows."""
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    get_window = kernel32.GetConsoleWindow
    show_window = user32.ShowWindow
    
    window_handle = get_window()
    if window_handle:
        show_window(window_handle, 0)  # SW_HIDE = 0

def main():
    # When packaged with PyInstaller, the entry point gets executed directly rather than
    # through the module system, which breaks imports. We need to re-launch in the correct
    # environment to ensure proper module resolution. Additionally, Windows Terminal
    # provides better Unicode support than the cmd.exe shell PyInstaller uses by default.
    if platform.system().lower() == "windows":
        if not os.environ.get("WT_SESSION"):
            args = [sys.executable] + sys.argv
            
            try:
                # Hide the console window
                hide_console()
                
                # Start Windows Terminal and wait for it to complete
                process = subprocess.Popen(
                    ["wt.exe", "--"] + args,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                process.wait()
                
                # Exit immediately after subprocess completes
                sys.exit(0)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fall back to direct execution if Windows Terminal isn't available
                pass
    
    import portstudy.cli.main
    portstudy.cli.main.main()

if __name__ == "__main__":
    main()