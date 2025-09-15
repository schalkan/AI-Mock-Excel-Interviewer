# Integration tests

import unittest
import os
from src.services.question_generator import QuestionGenerator
from src.services.answer_evaluator import AnswerEvaluator
from src.models.interview import InterviewSession, CandidateInfo
from config.settings import settings

class TestExcelInterviewer(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        os.environ["ENVIRONMENT"] = "testing"
        self.question_generator = QuestionGenerator()
        self.answer_evaluator = AnswerEvaluator()
        self.interview = InterviewSession()
        
    def test_interview_flow(self):
        """Test complete interview flow"""
        # Setup candidate
        candidate = CandidateInfo(
            name="Test Candidate",
            email="test@example.com",
            position_applied="Excel Analyst",
            experience_level="Intermediate"
        )
        self.interview.candidate_info = candidate
        
        # Start interview
        self.interview.start_interview()
        self.assertEqual(self.interview.status.value, "in_progress")
        
        # Test question generation
        question = self.question_generator.get_next_question(
            target_difficulty=5.0,
            used_categories=[]
        )
        self.assertIsNotNone(question)
        self.interview.set_current_question(question)
        
        # Test answer evaluation
        sample_answer = "To sum values in Excel, use the SUM function: =SUM(A1:A10)"
        evaluation = self.answer_evaluator.evaluate_response(question, sample_answer)
        self.assertIsNotNone(evaluation)
        self.assertTrue(0 <= evaluation.overall_score <= 10)
        
        # Complete interview
        self.interview.complete_interview()
        self.assertEqual(self.interview.status.value, "completed")
        
    def test_ai_question_generation(self):
        """Test AI-powered question generation"""
        question = self.question_generator.generate_ai_question(
            difficulty=5.0,
            category="basic_formulas"
        )
        self.assertIsNotNone(question)
        self.assertTrue(hasattr(question, 'text'))
        self.assertTrue(hasattr(question, 'expected_answer'))
        
    def test_evaluation_scoring(self):
        """Test answer evaluation scoring"""
        question = self.question_generator.get_next_question(target_difficulty=5.0)
        perfect_answer = question.expected_answer
        evaluation = self.answer_evaluator.evaluate_response(question, perfect_answer)
        
        self.assertGreaterEqual(evaluation.technical_score, 7.0)
        self.assertGreaterEqual(evaluation.overall_score, 7.0)
        
    def test_fallback_handling(self):
        """Test fallback mechanisms when AI is unavailable"""
        # Simulate AI service unavailable
        self.answer_evaluator.client = None
        
        question = self.question_generator.get_next_question(target_difficulty=5.0)
        answer = "Test answer"
        evaluation = self.answer_evaluator.evaluate_response(question, answer)
        
        self.assertIsNotNone(evaluation)
        self.assertTrue(hasattr(evaluation, 'overall_score'))

if __name__ == '__main__':
    unittest.main()
