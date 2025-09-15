from typing import List
from config.settings import settings

class DifficultyManager:
    """Manages adaptive difficulty scaling based on performance patterns"""
    
    def __init__(self):
        self.current_difficulty = settings.DEFAULT_DIFFICULTY
        self.performance_history: List[float] = []
        self.min_difficulty = settings.MIN_DIFFICULTY
        self.max_difficulty = settings.MAX_DIFFICULTY
    
    def calculate_adjustment(self, response_quality: float, time_taken: float, question_difficulty: float) -> float:
        """
        Intelligent difficulty adjustment considering multiple factors:
        - Answer accuracy and completeness
        - Response time relative to question complexity
        - Historical performance in similar categories
        - Recovery patterns after incorrect answers
        """
        base_adjustment = 0.0
        
        # Performance-based adjustment
        if response_quality >= 0.8:  # Strong performance
            base_adjustment = 1.5
        elif response_quality >= 0.6:  # Good performance
            base_adjustment = 0.5
        elif response_quality >= 0.4:  # Weak performance
            base_adjustment = -1.0
        else:  # Poor performance
            base_adjustment = -2.0
        
        # Time factor (reasonable time expectations)
        expected_time = question_difficulty * 30  # 30 seconds per difficulty point
        if time_taken < expected_time * 0.7:  # Very fast
            base_adjustment += 0.5
        elif time_taken > expected_time * 2:  # Very slow
            base_adjustment -= 0.5
        
        # Historical performance consideration
        self.performance_history.append(response_quality)
        if len(self.performance_history) >= 3:
            recent_trend = self._calculate_trend()
            if recent_trend > 0.1:  # Improving
                base_adjustment += 0.3
            elif recent_trend < -0.1:  # Declining
                base_adjustment -= 0.3
        
        # Calculate new difficulty
        new_difficulty = max(self.min_difficulty, 
                           min(self.max_difficulty, 
                               self.current_difficulty + base_adjustment))
        
        self.current_difficulty = new_difficulty
        return new_difficulty
    
    def _calculate_trend(self) -> float:
        """Calculate recent performance trend"""
        if len(self.performance_history) < 3:
            return 0.0
        
        recent = self.performance_history[-3:]
        return (recent[-1] - recent[0]) / 2
    
    def get_difficulty_category(self, difficulty: float) -> str:
        """Get difficulty category name"""
        if difficulty <= 3:
            return "Basic"
        elif difficulty <= 6:
            return "Intermediate"
        elif difficulty <= 8:
            return "Advanced"
        else:
            return "Expert"
    
    def reset(self):
        """Reset difficulty manager for new interview"""
        self.current_difficulty = settings.DEFAULT_DIFFICULTY
        self.performance_history = []