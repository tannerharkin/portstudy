"""Display utilities for the PortStudy application."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from typing import Dict, Any, List, Optional
from colorama import Fore, Style, init

from ..config.settings import ACCURACY_COLOR_THRESHOLDS, ASCII_ART
from ..core.game_state import GameState

# Initialize colorama
init(autoreset=True)

def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_accuracy_color(accuracy: float) -> str:
    """
    Get the appropriate color for displaying an accuracy value.
    
    Args:
        accuracy: Accuracy percentage value
        
    Returns:
        Colorama color code for the accuracy level
    """
    for threshold, color in ACCURACY_COLOR_THRESHOLDS:
        if accuracy >= threshold:
            return getattr(Fore, color)
    return Fore.RED

def display_level_progress(
    current_difficulty: int,
    accuracy_window: List[bool],
    streak_window: List[bool],
    level_requirements: Dict[int, Dict[str, Optional[int]]]
) -> None:
    """
    Display progress towards next level.
    
    Args:
        current_difficulty: Current difficulty level
        accuracy_window: List of recent accuracy results
        streak_window: List of streak data
        level_requirements: Dictionary of level requirements
    """
    if current_difficulty == max(level_requirements.keys()):
        print(f"\n{Fore.GREEN}Maximum level reached!{Style.RESET_ALL}")
        return

    current_reqs = level_requirements[current_difficulty]
    window_size = current_reqs["window"]
    
    if not accuracy_window:
        current_accuracy = 0
    else:
        correct = sum(1 for q in accuracy_window if q)
        current_accuracy = (correct / len(accuracy_window)) * 100
    
    current_streak = len(streak_window)
    min_streak = current_reqs["streak"]
    accuracy_required = current_reqs["accuracy"]
    
    print(f"\n{Fore.CYAN}Level {current_difficulty} Progress:{Style.RESET_ALL}")
    
    # Show streak progress bar
    width = 50
    progress = min(1.0, current_streak / min_streak) if min_streak else 0
    filled = int(width * progress)
    
    if current_accuracy >= accuracy_required:
        progress_bar = (Fore.GREEN + '█' * filled + 
                       Fore.WHITE + '░' * (width - filled))
    else:
        progress_bar = Fore.RED + '░' * width
        
    print(f"Streak Progress: |{progress_bar}{Fore.WHITE}| {current_streak}/{min_streak}")
    
    # Show scaled accuracy window visualization
    if window_size:
        # Fixed display width
        display_width = width  # Bar width for visualization
        block_size = max(1, len(accuracy_window) // display_width)  # Scale data to fit

        # Initialize blocks list
        blocks = [None] * display_width  # Placeholder for the entire bar

        # Traverse the accuracy_window backward and fill blocks right-to-left
        for i in range(display_width):
            start_idx = max(0, len(accuracy_window) - (i + 1) * block_size)
            end_idx = len(accuracy_window) - i * block_size
            if start_idx >= end_idx:
                break  # No more data to process

            # Check this segment of the data
            block = accuracy_window[start_idx:end_idx]
            if any(not result for result in block):
                blocks[display_width - 1 - i] = False  # At least one wrong in this segment
            elif block:  # Ensure block isn't empty
                blocks[display_width - 1 - i] = True  # All correct

        # Build the visualization string
        accuracy_bar = ""
        for block in blocks:
            if block is None:
                accuracy_bar += Fore.WHITE + '·'  # Placeholder for no data
            elif block:
                accuracy_bar += Fore.GREEN + '█'  # Correct answers
            else:
                accuracy_bar += Fore.RED + '█'  # Incorrect answers

        # Show block size in the label if it's greater than 1
        window_label = f"{len(accuracy_window)}/{window_size}"
        if block_size > 1:
            window_label += f" ({block_size}/□)"

        print(f"Recent Results:  |{accuracy_bar}{Fore.WHITE}| {window_label}")
    
    # Show accuracy information
    accuracy_color = get_accuracy_color(current_accuracy)
    print(f"Current Window Accuracy: {accuracy_color}{current_accuracy:.1f}%{Style.RESET_ALL}")
    print(f"Required Accuracy: {accuracy_required}%")
    
    # Show status message
    if current_accuracy < accuracy_required:
        print(f"{Fore.RED}Accuracy below {accuracy_required}% - streak reset!{Style.RESET_ALL}")
    elif current_streak < min_streak:
        remaining = min_streak - current_streak
        print(f"Maintain {accuracy_required}% accuracy for {remaining} more questions to advance")

def display_statistics(session_data: Dict[str, Any], game_state: GameState) -> None:
    """
    Display current session statistics.
    
    Args:
        session_data: Dictionary containing session statistics
        game_state: Current game state
    """
    clear_screen()
    print(f"\n{Fore.CYAN}=== Current Session Statistics ==={Style.RESET_ALL}")
    
    total = session_data["total"]
    if total > 0:
        accuracy = (session_data["correct"] / total * 100)
        print(f"Questions Attempted: {total}")
        print(f"Correct Answers: {session_data['correct']}")
        print(f"Session Accuracy: {accuracy:.1f}%")
    else:
        print(f"{Fore.YELLOW}No questions attempted in current session.{Style.RESET_ALL}")
    
    print(f"Current Level: {game_state.current_difficulty}")

def display_main_menu() -> None:
    """Display the main menu ASCII art and options."""
    clear_screen()
    print(f"{Fore.CYAN}{'=' * 97}")
    print(f"{Fore.YELLOW}{ASCII_ART}")
    print(f"{Fore.CYAN}{'=' * 97}")

def display_reference_info(port: str, port_data: Dict[str, Any]) -> None:
    """
    Display reference information for a port.
    
    Args:
        port: Port number
        port_data: Dictionary containing port information
    """
    print(f"\n{Fore.CYAN}Reference Information:{Style.RESET_ALL}")
    print(f"Port: {port}")
    print(f"Protocol: {port_data['protocol']}")
    print(f"Transport: {port_data['transport']}")
    print(f"Usage: {port_data['common_usage']}")
