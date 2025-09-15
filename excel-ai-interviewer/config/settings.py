"""
Configuration settings for Excel AI Interviewer
"""
import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM Configuration"""
    provider: str = "gemini"  # gemini, openai, anthropic, local
    model_name: str = "gemini-pro"
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    temperature: float = 0.3
    max_tokens: int = 1000

    # Fallback configuration
    fallback_provider: str = "anthropic"
    fallback_model: str = "claude-3-sonnet-20240229"
    fallback_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

@dataclass 
class DatabaseConfig:
    """Database Configuration"""
    provider: str = "sqlite"  # sqlite, postgresql
    url: str = "sqlite:///excel_interviewer.db"
    # For production PostgreSQL:
    # url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/excel_db")
    
@dataclass
class InterviewConfig:
    """Interview Configuration"""
    max_questions: int = 5
    min_questions: int = 3
    initial_difficulty: float = 5.0
    difficulty_range: tuple = (1.0, 10.0)
    max_response_time: int = 300  # seconds
    
    # Scoring weights
    technical_weight: float = 0.4
    approach_weight: float = 0.3
    communication_weight: float = 0.3
    
    # Difficulty adjustment parameters
    strong_performance_threshold: float = 0.8
    weak_performance_threshold: float = 0.4
    difficulty_increase: float = 1.5
    difficulty_decrease: float = -2.0

@dataclass
class UIConfig:
    """UI Configuration"""
    page_title: str = "AI Excel Mock Interviewer"
    page_icon: str = "📊"
    layout: str = "wide"
    theme_color: str = "#1e3c72"
    
class Settings:
    """Main settings class"""
    
    def __init__(self):
        self.llm = LLMConfig()
        self.database = DatabaseConfig()
        self.interview = InterviewConfig()
        self.ui = UIConfig()
        
        # Environment-specific overrides
        self._load_environment_overrides()
    
    def _load_environment_overrides(self):
        """Load environment-specific settings"""
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            self.database.provider = "postgresql"
            self.database.url = os.getenv("DATABASE_URL", self.database.url)
            self.llm.temperature = 0.2  # More conservative in production
        
        elif env == "testing":
            self.database.url = "sqlite:///:memory:"
            self.interview.max_questions = 2  # Faster tests
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "llm": self.llm.__dict__,
            "database": self.database.__dict__,
            "interview": self.interview.__dict__,
            "ui": self.ui.__dict__
        }

# Global settings instance
settings = Settings()