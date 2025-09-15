"""
Question model and related data structures
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

class QuestionCategory(Enum):
    """Excel question categories"""
    BASIC_FORMULAS = "basic_formulas"
    DATA_MANIPULATION = "data_manipulation"
    DATA_ANALYSIS = "data_analysis"
    ADVANCED_FUNCTIONS = "advanced_functions" 
    AUTOMATION_VBA = "automation_vba"

class DifficultyLevel(Enum):
    """Difficulty level mappings"""
    BEGINNER = (1, 3)      # 1-3
    INTERMEDIATE = (4, 6)   # 4-6  
    ADVANCED = (7, 8)      # 7-8
    EXPERT = (9, 10)       # 9-10

@dataclass
class EvaluationCriteria:
    """Criteria for evaluating answers"""
    required_keywords: List[str] = field(default_factory=list)
    excel_functions: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)

@dataclass
class ExcelQuestion:
    """Excel interview question model"""
    question_id: str
    text: str
    category: QuestionCategory
    difficulty: int
    model_answer: str
    evaluation_criteria: EvaluationCriteria
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    avg_score: float = 0.0
    
    # Question effectiveness metrics
    discrimination_index: float = 0.0  # How well it separates skill levels
    reliability_score: float = 0.0     # Consistency of evaluation
    
    def __post_init__(self):
        """Validate question data after initialization"""
        if not (1 <= self.difficulty <= 10):
            raise ValueError("Difficulty must be between 1 and 10")
            
        if not self.text.strip():
            raise ValueError("Question text cannot be empty")
    
    def increment_usage(self):
        """Track question usage"""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def update_effectiveness_metrics(self, score: float, discrimination: float):
        """Update question effectiveness based on usage"""
        # Running average of scores
        if self.usage_count > 0:
            self.avg_score = ((self.avg_score * (self.usage_count - 1)) + score) / self.usage_count
        else:
            self.avg_score = score
            
        self.discrimination_index = discrimination
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "question_id": self.question_id,
            "text": self.text,
            "category": self.category.value,
            "difficulty": self.difficulty,
            "model_answer": self.model_answer,
            "evaluation_criteria": {
                "required_keywords": self.evaluation_criteria.required_keywords,
                "excel_functions": self.evaluation_criteria.excel_functions,
                "concepts": self.evaluation_criteria.concepts,
                "best_practices": self.evaluation_criteria.best_practices,
                "common_mistakes": self.evaluation_criteria.common_mistakes
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "usage_count": self.usage_count,
            "avg_score": self.avg_score,
            "discrimination_index": self.discrimination_index,
            "reliability_score": self.reliability_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExcelQuestion':
        """Create from dictionary"""
        criteria = EvaluationCriteria(
            required_keywords=data["evaluation_criteria"]["required_keywords"],
            excel_functions=data["evaluation_criteria"]["excel_functions"], 
            concepts=data["evaluation_criteria"]["concepts"],
            best_practices=data["evaluation_criteria"]["best_practices"],
            common_mistakes=data["evaluation_criteria"]["common_mistakes"]
        )
        
        question = cls(
            question_id=data["question_id"],
            text=data["text"],
            category=QuestionCategory(data["category"]),
            difficulty=data["difficulty"],
            model_answer=data["model_answer"],
            evaluation_criteria=criteria
        )
        
        # Set metadata
        question.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            question.updated_at = datetime.fromisoformat(data["updated_at"])
        question.usage_count = data.get("usage_count", 0)
        question.avg_score = data.get("avg_score", 0.0)
        question.discrimination_index = data.get("discrimination_index", 0.0)
        question.reliability_score = data.get("reliability_score", 0.0)
        
        return question

@dataclass
class QuestionFilter:
    """Filter criteria for question selection"""
    categories: Optional[List[QuestionCategory]] = None
    difficulty_range: Optional[tuple] = None
    min_discrimination: Optional[float] = None
    exclude_ids: List[str] = field(default_factory=list)
    limit: Optional[int] = None