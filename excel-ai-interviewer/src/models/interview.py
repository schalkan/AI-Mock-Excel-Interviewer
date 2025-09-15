"""
Interview session models and data structures
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

from .question import ExcelQuestion
from .evaluation import AnswerEvaluation

class InterviewStage(Enum):
    """Interview progression stages"""
    WELCOME = "welcome"
    QUESTIONING = "questioning" 
    COMPLETE = "complete"
    TERMINATED = "terminated"

class InterviewStatus(Enum):
    """Interview completion status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"

@dataclass
class CandidateInfo:
    """Candidate information"""
    name: str
    email: Optional[str] = None
    position_applied: str = ""
    experience_level: str = ""
    department: str = ""
    
    # Additional context
    linkedin_profile: Optional[str] = None
    resume_summary: Optional[str] = None
    referral_source: Optional[str] = None

@dataclass 
class ConversationTurn:
    """Single conversation exchange"""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    speaker: str = ""  # "interviewer" or "candidate"
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # For interviewer messages
    question_id: Optional[str] = None
    
    # For candidate messages  
    response_time: Optional[float] = None
    evaluation: Optional[AnswerEvaluation] = None

@dataclass
class InterviewMetrics:
    """Interview performance metrics"""
    total_questions: int = 0
    questions_answered: int = 0
    avg_response_time: float = 0.0
    difficulty_progression: List[float] = field(default_factory=list)
    
    # Score breakdowns
    technical_scores: List[float] = field(default_factory=list)
    approach_scores: List[float] = field(default_factory=list) 
    communication_scores: List[float] = field(default_factory=list)
    overall_scores: List[float] = field(default_factory=list)
    
    # Aggregate scores
    avg_technical: float = 0.0
    avg_approach: float = 0.0
    avg_communication: float = 0.0
    overall_score: float = 0.0
    
    def update_averages(self):
        """Recalculate average scores"""
        if self.technical_scores:
            self.avg_technical = sum(self.technical_scores) / len(self.technical_scores)
        if self.approach_scores:
            self.avg_approach = sum(self.approach_scores) / len(self.approach_scores)
        if self.communication_scores:
            self.avg_communication = sum(self.communication_scores) / len(self.communication_scores)
        if self.overall_scores:
            self.overall_score = sum(self.overall_scores) / len(self.overall_scores)

@dataclass
class InterviewSession:
    """Complete interview session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    candidate_info: Optional[CandidateInfo] = None
    
    # Session state
    stage: InterviewStage = InterviewStage.WELCOME
    status: InterviewStatus = InterviewStatus.IN_PROGRESS
    current_question: Optional[ExcelQuestion] = None
    
    # Conversation history
    conversation: List[ConversationTurn] = field(default_factory=list)
    
    # Interview data
    questions_asked: List[str] = field(default_factory=list)  # Question IDs
    current_difficulty: float = 5.0
    metrics: InterviewMetrics = field(default_factory=InterviewMetrics)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Final assessment
    final_recommendation: Optional[str] = None
    confidence_score: Optional[float] = None
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    
    def start_interview(self):
        """Mark interview as started"""
        self.started_at = datetime.now()
        self.stage = InterviewStage.QUESTIONING
        
    def complete_interview(self):
        """Mark interview as completed"""
        self.completed_at = datetime.now()
        self.stage = InterviewStage.COMPLETE
        self.status = InterviewStatus.COMPLETED
        self.metrics.update_averages()
    
    def add_conversation_turn(self, turn: ConversationTurn):
        """Add conversation turn and update metrics"""
        self.conversation.append(turn)
        
        # Update metrics if this is an evaluated response
        if turn.speaker == "candidate" and turn.evaluation:
            eval_data = turn.evaluation
            self.metrics.technical_scores.append(eval_data.technical_score)
            self.metrics.approach_scores.append(eval_data.approach_score)
            self.metrics.communication_scores.append(eval_data.communication_score)
            self.metrics.overall_scores.append(eval_data.overall_score)
            
            if turn.response_time:
                # Update average response time
                total_time = self.metrics.avg_response_time * self.metrics.questions_answered
                self.metrics.questions_answered += 1
                self.metrics.avg_response_time = (total_time + turn.response_time) / self.metrics.questions_answered
    
    def set_current_question(self, question: ExcelQuestion):
        """Set current question and track difficulty"""
        self.current_question = question
        self.questions_asked.append(question.question_id)
        self.metrics.total_questions += 1
        self.metrics.difficulty_progression.append(question.difficulty)
    
    def get_duration_minutes(self) -> Optional[float]:
        """Get interview duration in minutes"""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            return duration.total_seconds() / 60
        return None
    
    def get_completion_rate(self) -> float:
        """Get percentage of questions answered"""
        if self.metrics.total_questions == 0:
            return 0.0
        return (self.metrics.questions_answered / self.metrics.total_questions) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "candidate_info": self.candidate_info.__dict__ if self.candidate_info else None,
            "stage": self.stage.value,
            "status": self.status.value,
            "current_question": self.current_question.to_dict() if self.current_question else None,
            "conversation": [
                {
                    "turn_id": turn.turn_id,
                    "speaker": turn.speaker,
                    "message": turn.message,
                    "timestamp": turn.timestamp.isoformat(),
                    "question_id": turn.question_id,
                    "response_time": turn.response_time,
                    "evaluation": turn.evaluation.to_dict() if turn.evaluation else None
                }
                for turn in self.conversation
            ],
            "questions_asked": self.questions_asked,
            "current_difficulty": self.current_difficulty,
            "metrics": {
                "total_questions": self.metrics.total_questions,
                "questions_answered": self.metrics.questions_answered,
                "avg_response_time": self.metrics.avg_response_time,
                "difficulty_progression": self.metrics.difficulty_progression,
                "technical_scores": self.metrics.technical_scores,
                "approach_scores": self.metrics.approach_scores,
                "communication_scores": self.metrics.communication_scores,
                "overall_scores": self.metrics.overall_scores,
                "avg_technical": self.metrics.avg_technical,
                "avg_approach": self.metrics.avg_approach,
                "avg_communication": self.metrics.avg_communication,
                "overall_score": self.metrics.overall_score
            },
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "final_recommendation": self.final_recommendation,
            "confidence_score": self.confidence_score,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement
        }