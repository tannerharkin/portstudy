"""User interface package for PortStudy."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .display import (
    clear_screen,
    get_accuracy_color,
    display_level_progress,
    display_statistics,
    display_main_menu,
    display_reference_info
)
from .menu import MenuSystem

__all__ = [
    'clear_screen',
    'get_accuracy_color',
    'display_level_progress',
    'display_statistics',
    'display_main_menu',
    'display_reference_info',
    'MenuSystem'
]