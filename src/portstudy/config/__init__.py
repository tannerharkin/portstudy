"""Configuration package for PortStudy."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .settings import (
    LEVEL_REQUIREMENTS,
    QUESTION_CHOICES,
    REDEMPTION_CHANCE,
    ASCII_ART,
    MENU_OPTIONS,
    ACCURACY_COLOR_THRESHOLDS
)

__all__ = [
    'LEVEL_REQUIREMENTS',
    'QUESTION_CHOICES',
    'REDEMPTION_CHANCE',
    'QUESTION_TYPE_WEIGHTS',
    'PORT_DIFFICULTY_WEIGHTS',
    'SAVE_INTEGRITY_KEYS',
    'ASCII_ART',
    'MENU_OPTIONS',
    'ACCURACY_COLOR_THRESHOLDS'
]