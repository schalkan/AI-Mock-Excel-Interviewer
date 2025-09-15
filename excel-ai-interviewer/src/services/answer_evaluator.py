import json
from typing import Dict, Any
import google.generativeai as genai
from config.settings import settings
from src.models.question import Question
from src.models.evaluation import EvaluationResult

class AnswerEvaluator:
    """Evaluates candidate responses using Google's Gemini with fallback logic"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client if API key is available"""
        api_key = settings.llm.api_key
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(settings.llm.model_name)
                self.client = True
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                self.client = None
    
    def evaluate_response(self, question: Question, response: str) -> EvaluationResult:
        """Evaluate candidate response and return detailed feedback"""
        
        if not self.client:
            return self._fallback_evaluation(question, response)
        
        try:
            evaluation_prompt = self._create_evaluation_prompt(question, response)
            
            response = self.model.generate_content(evaluation_prompt)
            
            try:
                result_dict = json.loads(response.text)
                return self._dict_to_evaluation_result(result_dict)
            except json.JSONDecodeError:
                return self._fallback_evaluation(question, response)
                
        except Exception as e:
            print(f"Error in AI evaluation: {e}")
            return self._fallback_evaluation(question, response)
    
    def _create_evaluation_prompt(self, question: Question, response: str) -> str:
        """Create evaluation prompt for OpenAI"""
        return f"""
        You are an expert Excel interviewer evaluating a candidate's response.
        
        Question: {question.text}
        Category: {question.category}
        Difficulty Level: {question.difficulty}/10
        Expected Answer: {question.expected_answer}
        Candidate Response: {response}
        
        Evaluation Criteria: {', '.join(question.evaluation_criteria)}
        
        Please provide a JSON response with:
        1. technical_score (0-10): Technical accuracy of the answer
        2. approach_score (0-10): Quality of approach and methodology
        3. communication_score (0-10): Clarity of explanation
        4. overall_score (0-10): Overall assessment
        5. feedback: Detailed constructive feedback (2-3 sentences)
        6. strengths: Array of what the candidate did well
        7. areas_for_improvement: Array of specific areas to work on
        
        Be fair but thorough in your evaluation. Consider the difficulty level when scoring.
        """
    
    def _dict_to_evaluation_result(self, result_dict: Dict[str, Any]) -> EvaluationResult:
        """Convert dictionary to EvaluationResult object"""
        return EvaluationResult(
            technical_score=float(result_dict.get('technical_score', 0)),
            approach_score=float(result_dict.get('approach_score', 0)),
            communication_score=float(result_dict.get('communication_score', 0)),
            overall_score=float(result_dict.get('overall_score', 0)),
            feedback=str(result_dict.get('feedback', 'No feedback available')),
            strengths=list(result_dict.get('strengths', [])),
            areas_for_improvement=list(result_dict.get('areas_for_improvement', []))
        )
    
    def _fallback_evaluation(self, question: Question, response: str) -> EvaluationResult:
        """Simple rule-based evaluation when AI is not available"""
        response_lower = response.lower().strip()
        expected_lower = question.expected_answer.lower()
        
        # Simple keyword matching and heuristics
        technical_score = self._calculate_technical_score(response_lower, expected_lower, question)
        approach_score = self._calculate_approach_score(response, question)
        communication_score = self._calculate_communication_score(response)
        
        overall_score = (
            technical_score * settings.TECHNICAL_WEIGHT +
            approach_score * settings.APPROACH_WEIGHT +
            communication_score * settings.COMMUNICATION_WEIGHT
        ) / (settings.TECHNICAL_WEIGHT + settings.APPROACH_WEIGHT + settings.COMMUNICATION_WEIGHT) * 10
        
        return EvaluationResult(
            technical_score=technical_score,
            approach_score=approach_score,
            communication_score=communication_score,
            overall_score=overall_score,
            feedback=self._generate_fallback_feedback(technical_score, approach_score, communication_score),
            strengths=self._identify_strengths(technical_score, approach_score, communication_score),
            areas_for_improvement=self._identify_improvements(technical_score, approach_score, communication_score)
        )
    
    def _calculate_technical_score(self, response: str, expected: str, question: Question) -> float:
        """Calculate technical accuracy score"""
        score = 0
        
        # Keyword matching
        expected_words = set(expected.split())
        response_words = set(response.split())
        common_words = expected_words.intersection(response_words)
        
        if common_words:
            score += min(6, len(common_words) * 2)
        
        # Formula detection for formula-based questions
        if question.category in ['basic_formulas', 'data_analysis']:
            if '=' in response:
                score += 2
            if any(func in response.upper() for func in ['SUM', 'AVERAGE', 'VLOOKUP', 'INDEX', 'MATCH']):
                score += 2
        
        return min(10, score)
    
    def _calculate_approach_score(self, response: str, question: Question) -> float:
        """Calculate approach quality score"""
        score = 5  # Base score
        
        # Length consideration (more detailed = better approach)
        if len(response) > 100:
            score += 2
        elif len(response) > 50:
            score += 1
        
        # Structured thinking indicators
        if any(indicator in response.lower() for indicator in ['first', 'then', 'next', 'finally']):
            score += 1
        
        # Best practices mentioned
        if any(practice in response.lower() for practice in ['best practice', 'efficient', 'optimize']):
            score += 2
        
        return min(10, score)
    
    def _calculate_communication_score(self, response: str) -> float:
        """Calculate communication clarity score"""
        score = 5  # Base score
        
        # Clarity indicators
        if len(response.split('.')) > 1:  # Multiple sentences
            score += 2
        
        if len(response.split()) > 20:  # Adequate detail
            score += 2
        
        # Professional language
        if not any(word in response.lower() for word in ['um', 'uh', 'like', 'you know']):
            score += 1
        
        return min(10, score)
    
    def _generate_fallback_feedback(self, tech: float, approach: float, comm: float) -> str:
        """Generate simple feedback based on scores"""
        if tech >= 7 and approach >= 7:
            return "Good technical understanding with a solid approach. Keep up the good work!"
        elif tech >= 5:
            return "Shows basic understanding but could benefit from more detailed explanations."
        else:
            return "Consider reviewing the fundamentals and providing more comprehensive answers."
    
    def _identify_strengths(self, tech: float, approach: float, comm: float) -> list:
        """Identify candidate strengths"""
        strengths = []
        if tech >= 7:
            strengths.append("Strong technical knowledge")
        if approach >= 7:
            strengths.append("Good problem-solving approach")
        if comm >= 7:
            strengths.append("Clear communication")
        if not strengths:
            strengths.append("Attempted to provide an answer")
        return strengths
    
    def _identify_improvements(self, tech: float, approach: float, comm: float) -> list:
        """Identify areas for improvement"""
        improvements = []
        if tech < 6:
            improvements.append("Review Excel functions and formulas")
        if approach < 6:
            improvements.append("Think through problems step-by-step")
        if comm < 6:
            improvements.append("Provide more detailed explanations")
        return improvements