"""Game state management and progression tracking with save data integrity protection.

This module handles the management of game progress including difficulty levels, 
accuracy tracking, and streak maintenance. It includes mechanisms to prevent save
data tampering through CRC16 checksums and unique XOR keys for different data types.

The save data format uses a compact binary structure:
    - 2 bytes: CRC16 checksum XORed with type-specific key
    - 2 bytes: Data length (big-endian)
    - 1 byte:  Separator (0x00)
    - n bytes: Bitfield data padded to byte boundary

The entire binary structure is then base64 encoded for storage.
"""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import base64
from typing import Dict, List, Deque, Any
from collections import deque
from datetime import datetime
import zlib

from ..config.settings import SAVE_INTEGRITY_KEYS, LEVEL_REQUIREMENTS

class GameState:
    """Manages game state data with serialization and integrity protection.
    
    This class handles the core game state including difficulty progression,
    accuracy tracking, and streak maintenance. It provides methods for saving
    and loading state data with integrity checks to prevent tampering.
    
    The state data is stored in a compressed format using bitfields and includes
    checksums to ensure data integrity and prevent basic save data manipulation.
    
    Attributes:
        FORMAT_VERSION (int): Version identifier for save data format
        current_difficulty (int): Current difficulty level of the game
        accuracy_window (Deque[bool]): Recent accuracy history as sliding window
        streak_window (List[bool]): Current streak of correct answers
    """
    
    FORMAT_VERSION = 1
    
    def __init__(self) -> None:
        """Initialize a new game state with default values."""
        self.current_difficulty: int = 1
        self.accuracy_window: Deque[bool] = deque(maxlen=30)
        self.streak_window: List[bool] = []
    
    @staticmethod
    def _compute_checksum(data: bytes, key: int) -> int:
        """Compute a tamper-resistant checksum for save data.
        
        Calculates a CRC16 checksum (derived from CRC32) and XORs it with a
        type-specific key to prevent data reuse between different save fields.
        
        Args:
            data: Raw bytes to compute checksum for
            key: 2-byte XOR key
            
        Returns:
            16-bit checksum value XORed with provided key
        """
        crc = zlib.crc32(data) & 0xFFFF  # Get lower 16 bits for CRC16
        return crc ^ key
    
    @staticmethod
    def _bitfield_to_base64(window_data: List[bool], key: int) -> str:
        """Convert boolean data to a base64 string with integrity protection.
        
        Packs boolean values into a bitfield, adds length and checksum data,
        and encodes the result in base64. The resulting string includes integrity
        checks to detect tampering.
        
        Binary format:
            [2 bytes] XORed CRC16 checksum
            [2 bytes] Data length (big-endian)
            [1 byte]  Null separator
            [n bytes] Bitfield data (padded to byte boundary)
        
        Args:
            window_data: List of boolean values to encode
            key: 2-byte XOR key for checksum calculation
            
        Returns:
            Base64 encoded string containing the packed data and checksums
        """
        if not window_data:
            return ""
        
        # Convert to bits and pad to byte boundary
        bits = ''.join('1' if x else '0' for x in window_data)
        length = len(window_data)
        padded_bits = bits.ljust(((len(bits) + 7) // 8) * 8, '0')
        
        # Create component bytes
        length_bytes = length.to_bytes(2, 'big')  # 16-bit length
        separator = b'\0'
        bitfield_bytes = int(padded_bits, 2).to_bytes((len(padded_bits) + 7) // 8, 'big')
        
        # Compute checksum over data components
        data_for_checksum = length_bytes + separator + bitfield_bytes
        checksum = GameState._compute_checksum(data_for_checksum, key)
        checksum_bytes = checksum.to_bytes(2, 'big')
        
        # Combine all components and encode
        all_bytes = checksum_bytes + data_for_checksum
        return base64.b64encode(all_bytes).decode()
    
    @staticmethod
    def _base64_to_bitfield(encoded_data: str, key: int, maxlen: int) -> Deque[bool]:
        """Restore boolean data from a base64 string with integrity validation.
        
        Decodes and unpacks a base64 string created by _bitfield_to_base64,
        verifying data integrity through checksum validation.
        
        Args:
            encoded_data: Base64 encoded string to decode
            key: 2-byte XOR key for checksum validation
            maxlen: Maximum length for the resulting deque
            
        Returns:
            Deque containing the restored boolean values
            
        Raises:
            ValueError: If checksum validation fails indicating data tampering
        """
        if not encoded_data:
            return deque(maxlen=maxlen)
        
        # Decode base64
        all_bytes = base64.b64decode(encoded_data)
        
        # Extract components
        checksum_bytes = all_bytes[:2]
        length_bytes = all_bytes[2:4]
        separator = all_bytes[4:5]
        bitfield_bytes = all_bytes[5:]
        
        # Validate checksum
        data_for_checksum = length_bytes + separator + bitfield_bytes
        expected_checksum = GameState._compute_checksum(data_for_checksum, key)
        actual_checksum = int.from_bytes(checksum_bytes, 'big')
        
        if expected_checksum != actual_checksum:
            raise ValueError("State data integrity check failed. Save data is corrupted.")
        
        # Convert to bits and validate
        length = int.from_bytes(length_bytes, 'big')
        all_bits = bin(int.from_bytes(bitfield_bytes, 'big'))[2:].zfill(len(bitfield_bytes) * 8)
        valid_bits = all_bits[:length]
        
        # Create and return window entries
        return deque(
            [bit == '1' for bit in valid_bits],
            maxlen=maxlen
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert current state to a dictionary for storage.
        
        Creates a serializable dictionary containing the current game state,
        with boolean data compressed and integrity-protected.
        
        Returns:
            Dictionary containing version, timestamp, difficulty level, and
            integrity-protected window data
        """
        return {
            "version": self.FORMAT_VERSION,
            "timestamp": datetime.now().isoformat(),
            "difficulty": self.current_difficulty,
            "accuracy_window": self._bitfield_to_base64(
                list(self.accuracy_window),
                SAVE_INTEGRITY_KEYS["accuracy"]
            ),
            "streak_window": self._bitfield_to_base64(
                self.streak_window,
                SAVE_INTEGRITY_KEYS["streak"]
            )
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], window_sizes: Dict[int, int]) -> 'GameState':
        """Create a GameState instance from stored dictionary data.
        
        Args:
            data: Dictionary containing saved game state data
            window_sizes: Dictionary mapping difficulty levels to window sizes
            
        Returns:
            New GameState instance with restored data
            
        Raises:
            ValueError: If save format version is incompatible or data integrity
                        checks fail
        """
        if data.get("version", 1) != cls.FORMAT_VERSION:
            raise ValueError(f"Incompatible save format version: {data.get('version')}")
        
        state = cls()
        state.current_difficulty = data["difficulty"]
        
        # For max level, use the window size of the previous level
        if state.current_difficulty == max(LEVEL_REQUIREMENTS.keys()):
            window_size = window_sizes[state.current_difficulty - 1]
        else:
            window_size = window_sizes[state.current_difficulty]
            
        # Restore windows with integrity checks
        state.accuracy_window = cls._base64_to_bitfield(
            data["accuracy_window"],
            SAVE_INTEGRITY_KEYS["accuracy"],
            window_size
        )
        
        state.streak_window = list(cls._base64_to_bitfield(
            data["streak_window"],
            SAVE_INTEGRITY_KEYS["streak"],
            window_size
        ))
        
        return state
