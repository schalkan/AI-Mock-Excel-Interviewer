"""
Answer evaluation models and scoring structures
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class ScoreLevel(Enum):
    """Score level classifications"""
    EXCELLENT = (0.9, 1.0, "🟢")
    GOOD = (0.7, 0.89, "🟡") 
    SATISFACTORY = (0.5, 0.69, "🟠")
    NEEDS_IMPROVEMENT = (0.0, 0.49, "🔴")
    
    def __init__(self, min_score: float, max_score: float, emoji: str):
        self.min_score = min_score
        self.max_score = max_score
        self.emoji = emoji
    
    @classmethod
    def from_score(cls, score: float) -> 'ScoreLevel':
        """Get score level from numeric score"""
        for level in cls:
            if level.min_score <= score <= level.max_score:
                return level
        return cls.NEEDS_IMPROVEMENT

@dataclass
class ScoreBreakdown:
    """Detailed score breakdown for each dimension"""
    raw_score: float
    weighted_score: float
    level: ScoreLevel
    justification: str
    keywords_found: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    bonus_points: float = 0.0
    penalty_points: float = 0.0

@dataclass
class AnswerEvaluation:
    """Complete answer evaluation with detailed scoring"""
    answer_text: str
    question_id: str
    
    # Core scoring dimensions
    technical_score: float
    approach_score: float
    communication_score: float
    overall_score: float
    
    # Detailed breakdowns
    technical_breakdown: Optional[ScoreBreakdown] = None
    approach_breakdown: Optional[ScoreBreakdown] = None
    communication_breakdown: Optional[ScoreBreakdown] = None
    
    # Evaluation metadata
    evaluator_version: str = "1.0"
    evaluation_time: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.9
    
    # Feedback components
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    specific_feedback: str = ""
    
    # Advanced metrics
    response_completeness: float = 0.0
    accuracy_confidence: float = 0.0
    creativity_score: float = 0.0
    
    def __post_init__(self):
        """Calculate derived metrics after initialization"""
        self.response_completeness = self._calculate_completeness()
        
        # Set score levels for breakdowns
        if self.technical_breakdown:
            self.technical_breakdown.level = ScoreLevel.from_score(self.technical_score)
        if self.approach_breakdown:
            self.approach_breakdown.level = ScoreLevel.from_score(self.approach_score)
        if self.communication_breakdown:
            self.communication_breakdown.level = ScoreLevel.from_score(self.communication_score)
    
    def _calculate_completeness(self) -> float:
        """Calculate how complete the answer is"""
        if not self.answer_text:
            return 0.0
            
        # Basic completeness indicators
        word_count = len(self.answer_text.split())
        sentence_count = self.answer_text.count('.') + self.answer_text.count('!') + self.answer_text.count('?')
        
        completeness = 0.0
        
        # Word count factor (optimal range: 20-150 words)
        if 20 <= word_count <= 150:
            completeness += 0.4
        elif word_count > 10:
            completeness += 0.2
        
        # Structure factor
        if sentence_count >= 2:
            completeness += 0.3
        
        # Detail factor (presence of explanatory words)
        detail_words = ['because', 'since', 'therefore', 'however', 'although', 'first', 'then', 'next']
        if any(word in self.answer_text.lower() for word in detail_words):
            completeness += 0.3
            
        return min(1.0, completeness)
    
    def get_overall_level(self) -> ScoreLevel:
        """Get overall performance level"""
        return ScoreLevel.from_score(self.overall_score)
    
    def get_summary_feedback(self) -> str:
        """Generate concise summary feedback"""
        level = self.get_overall_level()
        
        feedback_templates = {
            ScoreLevel.EXCELLENT: "Outstanding response demonstrating strong Excel expertise.",
            ScoreLevel.GOOD: "Good understanding with solid Excel knowledge.",
            ScoreLevel.SATISFACTORY: "Adequate response with room for improvement.",
            ScoreLevel.NEEDS_IMPROVEMENT: "Response indicates need for Excel skill development."
        }
        
        base_feedback = feedback_templates[level]
        
        if self.strengths:
            base_feedback += f" Strengths: {', '.join(self.strengths[:2])}."
        
        if self.improvements:
            base_feedback += f" Focus areas: {', '.join(self.improvements[:2])}."
            
        return base_feedback
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "answer_text": self.answer_text,
            "question_id": self.question_id,
            "technical_score": self.technical_score,
            "approach_score": self.approach_score,
            "communication_score": self.communication_score,
            "overall_score": self.overall_score,
            "technical_breakdown": self._breakdown_to_dict(self.technical_breakdown),
            "approach_breakdown": self._breakdown_to_dict(self.approach_breakdown),
            "communication_breakdown": self._breakdown_to_dict(self.communication_breakdown),
            "evaluator_version": self.evaluator_version,
            "evaluation_time": self.evaluation_time.isoformat(),
            "confidence_score": self.confidence_score,
            "strengths": self.strengths,
            "improvements": self.improvements,
            "specific_feedback": self.specific_feedback,
            "response_completeness": self.response_completeness,
            "accuracy_confidence": self.accuracy_confidence,
            "creativity_score": self.creativity_score
        }
    
    def _breakdown_to_dict(self, breakdown: Optional[ScoreBreakdown]) -> Optional[Dict]:
        """Convert score breakdown to dictionary"""
        if not breakdown:
            return None
            
        return {
            "raw_score": breakdown.raw_score,
            "weighted_score": breakdown.weighted_score,
            "level": breakdown.level.name,
            "justification": breakdown.justification,
            "keywords_found": breakdown.keywords_found,
            "missing_elements": breakdown.missing_elements,
            "bonus_points": breakdown.bonus_points,
            "penalty_points": breakdown.penalty_points
        }

@dataclass
class EvaluationCriteria:
    """Evaluation criteria for a specific question type"""
    technical_keywords: List[str] = field(default_factory=list)
    required_functions: List[str] = field(default_factory=list)
    approach_indicators: List[str] = field(default_factory=list)
    communication_markers: List[str] = field(default_factory=list)
    
    # Scoring weights
    keyword_weight: float = 0.4
    function_weight: float = 0.3
    approach_weight: float = 0.3
    
    # Penalty factors
    common_mistakes: List[str] = field(default_factory=list)
    mistake_penalty: float = -0.2

@dataclass 
class EvaluationBenchmark:
    """Benchmark scores for calibration"""
    question_id: str
    expert_scores: List[float] = field(default_factory=list)
    ai_scores: List[float] = field(default_factory=list)
    sample_answers: List[str] = field(default_factory=list)
    
    def calculate_correlation(self) -> float:
        """Calculate correlation between expert and AI scores"""
        if len(self.expert_scores) != len(self.ai_scores) or len(self.expert_scores) < 2:
            return 0.0
        
        # Simple correlation calculation
        n = len(self.expert_scores)
        mean_expert = sum(self.expert_scores) / n
        mean_ai = sum(self.ai_scores) / n
        
        numerator = sum((expert - mean_expert) * (ai - mean_ai) 
                       for expert, ai in zip(self.expert_scores, self.ai_scores))
        
        expert_var = sum((expert - mean_expert) ** 2 for expert in self.expert_scores)
        ai_var = sum((ai - mean_ai) ** 2 for ai in self.ai_scores)
        
        denominator = (expert_var * ai_var) ** 0.5
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def get_average_difference(self) -> float:
        """Get average absolute difference between expert and AI scores"""
        if len(self.expert_scores) != len(self.ai_scores):
            return 0.0
        
        differences = [abs(expert - ai) for expert, ai in zip(self.expert_scores, self.ai_scores)]
        return sum(differences) / len(differences) if differences else 0.0