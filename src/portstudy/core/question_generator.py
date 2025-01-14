"""Question generation and management for the PortStudy application."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
from typing import Dict, List, Tuple, Any

from ..config.settings import (
    QUESTION_CHOICES,
    QUESTION_TYPE_WEIGHTS,
    PORT_DIFFICULTY_WEIGHTS
)

class QuestionGenerator:
    """Generates questions based on port information and difficulty levels."""
    
    def __init__(self, port_info: Dict[str, Dict[str, Any]]) -> None:
        """
        Initialize the question generator.
        
        Args:
            port_info: Dictionary containing port information
        """
        self.port_info = port_info
        self._categorize_ports()
    
    def _categorize_ports(self) -> None:
        """Categorize ports by difficulty level."""
        self.ports_by_difficulty = {
            "beginner": [],
            "intermediate": [],
            "advanced": []
        }
        
        for port, info in self.port_info.items():
            difficulty = info.get("difficulty", "intermediate")
            self.ports_by_difficulty[difficulty].append(port)
    
    def _get_available_ports(self, difficulty_level: int) -> List[str]:
        """
        Get available ports based on current difficulty level.
        
        Args:
            difficulty_level: Current difficulty level
            
        Returns:
            List of port numbers available at this level
        """
        available_ports = []
        
        # Level 1-2: Only beginner ports
        if difficulty_level <= 2:
            available_ports.extend(self.ports_by_difficulty["beginner"])
            
        # Level 3-4: Add intermediate ports
        if difficulty_level >= 3:
            available_ports.extend(self.ports_by_difficulty["beginner"])
            available_ports.extend(self.ports_by_difficulty["intermediate"])
            
        # Level 5: Add advanced ports
        if difficulty_level >= 5:
            available_ports.extend(self.ports_by_difficulty["advanced"])
        
        return available_ports
    
    def _select_port(self, difficulty_level: int) -> str:
        """
        Select a port based on difficulty level and weighting.
        
        Args:
            difficulty_level: Current difficulty level
            
        Returns:
            Selected port number as string
        """
        available_ports = self._get_available_ports(difficulty_level)
        
        # Create weighted list based on port difficulties
        weighted_ports = []
        for port in available_ports:
            difficulty = self.port_info[port]["difficulty"]
            weight = PORT_DIFFICULTY_WEIGHTS[difficulty]
            weighted_ports.extend([port] * weight)
        
        return random.choice(weighted_ports)
    
    def generate_port_entry_question(self, port_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a direct port entry question.
        
        Args:
            port_info: Dictionary containing port information
            
        Returns:
            Dictionary containing question data
        """
        return {
            "question": f"What port number does {port_info['protocol']} use?",
            "correct_answer": port_info["port"],
            "type": "port_entry",
            "port_entry": True,
            "port": port_info["port"],
            "port_data": port_info
        }
    
    def generate_choices(self, correct_answer: Any, question_type: str, difficulty: int) -> List[Any]:
        """Generate multiple choice options for a question."""
        choices: List[Any] = []
        
        if question_type == "port":
            correct_port = str(correct_answer)
            if difficulty >= 3 and 'similar_ports' in self.port_info[correct_port]:
                similar_ports = self.port_info[correct_port]['similar_ports']
                choices = random.sample(similar_ports, 
                                     min(len(similar_ports), QUESTION_CHOICES - 1))
            else:
                available_ports = self._get_available_ports(difficulty)
                choices = random.sample([p for p in available_ports if p != correct_port], 
                                     QUESTION_CHOICES - 1)
                choices = [int(p) for p in choices]
        
        elif question_type == "protocol":
            all_protocols = [info["protocol"] for info in self.port_info.values()]
            choices = random.sample([p for p in all_protocols if p != correct_answer], 
                                 QUESTION_CHOICES - 1)
        
        elif question_type == "transport":
            choices = ["TCP", "UDP", "TCP/UDP"]
            if correct_answer in choices:
                choices.remove(correct_answer)
                
        elif question_type == "common_usage":
            all_usages = list(set(info["common_usage"] for info in self.port_info.values()))
            choices = random.sample([u for u in all_usages if u != correct_answer],
                                 QUESTION_CHOICES - 1)
                                 
        elif question_type == "description":
            all_descriptions = list(set(info.get("description", "") for info in self.port_info.values()))
            all_descriptions = [d for d in all_descriptions if d and d != correct_answer]
            choices = random.sample(all_descriptions, min(len(all_descriptions), QUESTION_CHOICES - 1))
        
        choices.append(correct_answer)
        random.shuffle(choices)
        return choices

    def generate_question(self, difficulty: int) -> Dict[str, Any]:
        """
        Generate a question based on difficulty level.
        
        Args:
            difficulty: Current difficulty level
            
        Returns:
            Dictionary containing question data
        """
        # Select question type based on weights and level
        if difficulty >= 4:
            question_type = random.choices(
                ["standard", "port_entry"],
                weights=[QUESTION_TYPE_WEIGHTS["standard"], QUESTION_TYPE_WEIGHTS["port_entry"]]
            )[0]
        else:
            question_type = "standard"
        
        # Select a port and get its data
        port = self._select_port(difficulty)
        port_data = self.port_info[port].copy()
        port_data['port'] = port
        
        # Generate port entry question if selected
        if question_type == "port_entry":
            return self.generate_port_entry_question(port_data)
        
        # Generate standard multiple choice question
        question_types: List[Tuple[str, str, str]] = []
        
        # Level 1: Basic port/protocol pairs
        if difficulty >= 1:
            question_types.extend([
                ("port_to_protocol", "What protocol uses port {port}?", "protocol"),
                ("protocol_to_port", "What port number does {protocol} use?", "port")
            ])
        
        # Level 2: Add transport protocols
        if difficulty >= 2:
            question_types.append(
                ("protocol_to_transport", "What transport protocol does {protocol} use?", "transport")
            )
        
        # Level 3+: More complex questions
        if difficulty >= 3:
            question_types.extend([
                ("port_usage", "What is the primary usage of port {port}?", "common_usage"),
                ("protocol_description", "Which best describes {protocol}?", "description")
            ])
        
        question_type, template, answer_type = random.choice(question_types)
        
        return {
            "question": template.format(**port_data),
            "correct_answer": port_data[answer_type],
            "choices": self.generate_choices(port_data[answer_type], answer_type, difficulty),
            "type": answer_type,
            "port_entry": False,
            "port": port,
            "port_data": port_data
        }
