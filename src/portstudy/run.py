"""Bootstrap for PyInstaller binary to launch program in Windows Terminal."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import subprocess
import platform
import os

def main():
    # When packaged with PyInstaller, the entry point gets executed directly rather than
    # through the module system, which breaks imports. We need to re-launch in the correct
    # environment to ensure proper module resolution. Additionally, Windows Terminal
    # provides better Unicode support than the cmd.exe shell PyInstaller uses by default.
    if platform.system().lower() == "windows":
        if not os.environ.get("WT_SESSION"):
            args = [sys.executable] + sys.argv
            
            try:
                subprocess.run(["wt.exe", "--"] + args, check=True)
                sys.exit(0)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fall back to direct execution if Windows Terminal isn't available
                pass
    
    import portstudy.cli.main
    portstudy.cli.main.main()

if __name__ == "__main__":
    main()