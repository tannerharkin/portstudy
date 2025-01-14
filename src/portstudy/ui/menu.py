"""Menu system and practice mode implementation."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time
from collections import deque
from typing import Dict, Any, Optional
from datetime import datetime
from colorama import Fore, Style

from ..config.settings import MENU_OPTIONS, LEVEL_REQUIREMENTS
from ..core.state_manager import StateManager
from ..core.question_generator import QuestionGenerator
from .display import (
    clear_screen,
    display_main_menu,
    display_statistics,
    display_level_progress,
    display_reference_info
)

class MenuSystem:
    """Handles menu navigation and practice mode implementation."""
    
    def __init__(
        self,
        port_info: Dict[str, Dict[str, Any]],
        state_manager: StateManager,
        question_gen: QuestionGenerator
    ) -> None:
        self.port_info = port_info
        self.state_manager = state_manager
        self.question_gen = question_gen
        
        # Load game state
        window_sizes = {
            level: req["window"] 
            for level, req in LEVEL_REQUIREMENTS.items() 
            if req["window"] is not None
        }
        self.game_state = state_manager.load_state(window_sizes)
        
        # Initialize session statistics
        self.current_session = {
            "start_time": datetime.now(),
            "correct": 0,
            "total": 0
        }
        self.questions_answered = 0
    
    def main_menu(self) -> None:
        """Run the main menu interface."""
        while True:
            try:
                display_main_menu()
                print(f"{Fore.GREEN}Current Level: {self.game_state.current_difficulty}")
                
                print(f"\n{Fore.CYAN}Choose your study mode:{Style.RESET_ALL}")
                for key, value in MENU_OPTIONS.items():
                    print(f"{key}. {value}")
                
                choice = input(f"\n{Fore.GREEN}Select an option (1-{len(MENU_OPTIONS)}):{Style.RESET_ALL} ").strip()
                
                if choice == "1":
                    self.practice_mode()
                elif choice == "2":
                    display_statistics(self.current_session, self.game_state)
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                elif choice == "3":
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                    time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
                time.sleep(1)
                continue
        
        print(f"\n\n{Fore.GREEN}Thanks for studying! Saving progress...{Style.RESET_ALL}")
        self.state_manager.save_state(self.game_state)
    
    def practice_mode(self) -> None:
        """Run the practice mode session."""
        try:
            clear_screen()
            print(f"{Fore.CYAN}=== Practice Mode ==={Style.RESET_ALL}")
            print("Maintain the required accuracy to advance!")
            print(f"{Fore.YELLOW}Type 'q' at any time to quit{Style.RESET_ALL}")
            time.sleep(2)
            
            while True:
                try:
                    self._run_practice_question()
                    input(f"\n{Fore.CYAN}Press Enter for next question...{Style.RESET_ALL}")
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"{Fore.RED}Error in practice question: {e.__class__.__name__}: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Press Enter to try another question...{Style.RESET_ALL}")
                    input()
                    continue
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Study session ended. Saving progress...{Style.RESET_ALL}")
            self.state_manager.save_state(self.game_state)
    
    def _get_user_answer(self, num_choices: Optional[int] = None) -> Optional[int]:
        """Get and validate user input for question answers."""
        while True:
            try:
                if num_choices:
                    user_input = input(
                        f"\n{Fore.GREEN}Enter your choice (1-{num_choices} or 'q' to quit):{Style.RESET_ALL} "
                    )
                else:
                    user_input = input(
                        f"\n{Fore.GREEN}Enter the port number (or 'q' to quit):{Style.RESET_ALL} "
                    )
                
                if user_input.lower() == 'q':
                    return None
                
                answer = int(user_input)
                if num_choices:
                    if 1 <= answer <= num_choices:
                        return answer
                    print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                else:
                    if 1 <= answer <= 65535:  # Valid port range
                        return answer
                    print(f"{Fore.RED}Invalid port number. Must be between 1 and 65535.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number or 'q' to quit.{Style.RESET_ALL}")
    
    def _run_practice_question(self) -> None:
        """Run a single practice question."""
        clear_screen()
        self.questions_answered += 1
        
        # Generate question for current difficulty
        question_data = self.question_gen.generate_question(self.game_state.current_difficulty)
        
        # Display question
        print(f"{Fore.CYAN}=== Practice Mode ==={Style.RESET_ALL}")
        print(f"{Fore.GREEN}Current Level: {self.game_state.current_difficulty}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Question {self.questions_answered}{Style.RESET_ALL}")
        print(f"\n{question_data['question']}")
        
        if question_data.get('port_entry'):
            answer = self._get_user_answer()
        else:
            for idx, choice in enumerate(question_data['choices'], 1):
                print(f"{idx}. {choice}")
            answer = self._get_user_answer(len(question_data['choices']))
        
        if answer is None:
            raise KeyboardInterrupt
        
        if question_data.get('port_entry'):
            user_answer = str(answer)
        else:
            user_answer = question_data['choices'][answer - 1]
        
        is_correct = user_answer == question_data['correct_answer']
        
        self._process_answer(is_correct, question_data)
        display_reference_info(question_data['port'], question_data['port_data'])
        display_level_progress(
            self.game_state.current_difficulty,
            list(self.game_state.accuracy_window),
            self.game_state.streak_window,
            LEVEL_REQUIREMENTS
        )
        self.state_manager.save_state(self.game_state)
    
    def check_level_progress(self, is_correct: bool) -> bool:
        """Check if user should level up based on streak and accuracy."""
        if self.game_state.current_difficulty == max(LEVEL_REQUIREMENTS.keys()):
            return False

        # Add new question to accuracy window
        self.game_state.accuracy_window.append(is_correct)

        # Get current level requirements
        level_reqs = LEVEL_REQUIREMENTS[self.game_state.current_difficulty]
        
        # Calculate current accuracy
        if not self.game_state.accuracy_window:
            return False
            
        correct = sum(1 for q in self.game_state.accuracy_window if q)
        current_accuracy = (correct / len(self.game_state.accuracy_window)) * 100
        
        # Update streak window
        if current_accuracy >= level_reqs["accuracy"]:
            if is_correct:
                self.game_state.streak_window.append(True)
        else:
            self.game_state.streak_window = []
        
        # Check if requirements are met for level up
        if (len(self.game_state.streak_window) >= level_reqs["streak"] and 
            current_accuracy >= level_reqs["accuracy"]):
            # Level up
            self.game_state.current_difficulty += 1
            
            # Reset windows for new level
            self.game_state.streak_window = []
            self.game_state.accuracy_window.clear()
            
            # Set new window size if not max level
            if self.game_state.current_difficulty < max(LEVEL_REQUIREMENTS.keys()):
                new_size = LEVEL_REQUIREMENTS[self.game_state.current_difficulty]["window"]
                self.game_state.accuracy_window = deque(maxlen=new_size)
            
            return True
        
        return False
    
    def check_difficulty_regression(self) -> bool:
        """Check if difficulty should decrease due to sustained poor performance.
        
        Only triggers regression if:
        1. Current difficulty is above level 1
        2. We have a meaningful sample size (at least 1/3 of the window filled)
        3. Recent accuracy is under 10% below the requirement for previous level
        
        Returns:
            bool: True if difficulty decreased, False otherwise
        """
        if self.game_state.current_difficulty <= 1:
            return False
            
        if not self.game_state.accuracy_window:
            return False
        
        # Only check regression after accumulating meaningful data
        min_samples = max(5, self.game_state.accuracy_window.maxlen // 3)
        if len(self.game_state.accuracy_window) < min_samples:
            return False
            
        correct = sum(1 for q in self.game_state.accuracy_window if q)
        recent_accuracy = (correct / len(self.game_state.accuracy_window)) * 100
        
        if recent_accuracy < LEVEL_REQUIREMENTS[self.game_state.current_difficulty - 1]["accuracy"] - 10:
            self.game_state.current_difficulty -= 1
            
            # Reset windows for new level
            self.game_state.streak_window = []
            new_size = LEVEL_REQUIREMENTS[self.game_state.current_difficulty]["window"]
            self.game_state.accuracy_window = deque(maxlen=new_size)
            return True
            
        return False
    
    def _process_answer(self, is_correct: bool, question_data: Dict[str, Any]) -> None:
        """Process and handle a user's answer."""
        if is_correct:
            print(f"\n{Fore.GREEN}✓ Correct!{Style.RESET_ALL}")
            self.current_session["correct"] += 1
            self.current_session["total"] += 1
            
            if self.check_level_progress(True):
                print(f"\n{Fore.GREEN}🎉 Level Up! You've advanced to level {self.game_state.current_difficulty}!{Style.RESET_ALL}")
                print("You've consistently maintained the required accuracy. Great job!")
        else:
            print(f"\n{Fore.RED}✗ Incorrect. The correct answer is {question_data['correct_answer']}{Style.RESET_ALL}")
            self.current_session["total"] += 1
            
            self.check_level_progress(False)
            if self.check_difficulty_regression():
                print(f"\n{Fore.YELLOW}⚠ Difficulty decreased to level {self.game_state.current_difficulty} due to accuracy drop.{Style.RESET_ALL}")
