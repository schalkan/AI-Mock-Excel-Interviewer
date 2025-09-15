import google.generativeai as genai
from config.settings import settings
from typing import Optional, List
from src.models.question import Question
from src.data.question_bank import QuestionBank
import uuid

class QuestionGenerator:
    """Manages question selection and generation logic"""
    
    def __init__(self):
        self.question_bank = QuestionBank()
        self.used_questions: List[str] = []
        self._init_ai()
    
    def _init_ai(self):
        """Initialize Gemini AI"""
        try:
            genai.configure(api_key=settings.llm.api_key)
            self.model = genai.GenerativeModel(settings.llm.model_name)
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini: {e}")
            self.model = None

    def generate_ai_question(self, difficulty: float, category: str) -> Optional[Question]:
        """Generate a new question using Gemini AI"""
        if not self.model:
            return None
            
        prompt = f"""
        Generate an Excel interview question with the following specifications:
        - Difficulty level: {difficulty}/10
        - Category: {category}
        - Include a clear question
        - Include the expected answer
        - Include 3-5 evaluation criteria
        
        Format the response as a JSON object with these fields:
        - question_text: the interview question
        - expected_answer: the model answer
        - evaluation_criteria: array of criteria
        """
        
        try:
            response = self.model.generate_content(prompt)
            question_data = response.text
            
            # Parse the response and create Question object
            return Question(
                question_id=str(uuid.uuid4()),
                text=question_data.get('question_text', ''),
                category=category,
                difficulty=difficulty,
                expected_answer=question_data.get('expected_answer', ''),
                evaluation_criteria=question_data.get('evaluation_criteria', [])
            )
        except Exception as e:
            print(f"Error generating question: {e}")
            return None

    def get_next_question(self, target_difficulty: float, used_categories: List[str] = None, 
                         preferred_category: str = None) -> Optional[Question]:
        """Get next question from bank or generate using AI"""
        # Try getting from question bank first
        question = super().get_next_question(target_difficulty, used_categories, preferred_category)
        
        # If no question found and AI is available, try generating one
        if not question and self.model:
            target_category = self._select_target_category(
                self.question_bank.get_categories(),
                used_categories or [],
                preferred_category
            )
            question = self.generate_ai_question(target_difficulty, target_category)
            
        if question:
            self.used_questions.append(question.question_id)
            
        return question
    
    def _select_target_category(self, all_categories: List[str], 
                               used_categories: List[str], 
                               preferred_category: str = None) -> Optional[str]:
        """Select the best category for the next question"""
        
        # If preferred category is specified and available, use it
        if preferred_category and preferred_category in all_categories:
            return preferred_category
        
        # Prioritize unused categories for comprehensive coverage
        unused_categories = [cat for cat in all_categories if cat not in used_categories]
        
        if unused_categories:
            # Return first unused category (following priority order)
            return unused_categories[0]
        
        # If all categories used, cycle through them
        return all_categories[len(used_categories) % len(all_categories)] if all_categories else None
    
    def get_category_coverage(self, asked_questions: List[Question]) -> dict:
        """Get coverage statistics for each category"""
        coverage = {}
        all_categories = self.question_bank.get_categories()
        
        for category in all_categories:
            asked_in_category = len([q for q in asked_questions if q.category == category])
            total_in_category = len(self.question_bank.get_questions_by_category(category))
            coverage[category] = {
                'asked': asked_in_category,
                'total': total_in_category,
                'percentage': (asked_in_category / total_in_category * 100) if total_in_category > 0 else 0
            }
        
        return coverage
    
    def reset_session(self):
        """Reset for new interview session"""
        self.used_questions = []
    
    def get_difficulty_distribution(self, questions: List[Question]) -> dict:
        """Get difficulty distribution of asked questions"""
        if not questions:
            return {}
        
        difficulties = [q.difficulty for q in questions]
        return {
            'min': min(difficulties),
            'max': max(difficulties),
            'average': sum(difficulties) / len(difficulties),
            'count': len(difficulties)
        }