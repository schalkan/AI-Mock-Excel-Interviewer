import unittest
from unittest.mock import patch, MagicMock
from src.services.question_generator import QuestionGenerator
from src.services.answer_evaluator import AnswerEvaluator
from src.models.question import ExcelQuestion
from src.models.evaluation import AnswerEvaluation

class TestQuestionGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = QuestionGenerator()
    
    def test_get_next_question(self):
        """Test question selection logic"""
        question = self.generator.get_next_question(
            target_difficulty=5.0,
            used_categories=[]
        )
        self.assertIsNotNone(question)
        self.assertIsInstance(question, ExcelQuestion)
        self.assertGreaterEqual(question.difficulty, 1.0)
        self.assertLessEqual(question.difficulty, 10.0)

    def test_category_coverage(self):
        """Test category tracking"""
        questions = [
            ExcelQuestion(question_id="1", category="formulas", difficulty=5.0),
            ExcelQuestion(question_id="2", category="pivot_tables", difficulty=6.0)
        ]
        coverage = self.generator.get_category_coverage(questions)
        self.assertIn("formulas", coverage)
        self.assertIn("pivot_tables", coverage)

    @patch('google.generativeai.GenerativeModel')
    def test_ai_generation(self, mock_ai):
        """Test AI-powered question generation"""
        mock_response = MagicMock()
        mock_response.text = {
            'question_text': 'Test question',
            'expected_answer': 'Test answer',
            'evaluation_criteria': ['criteria1']
        }
        mock_ai.return_value.generate_content.return_value = mock_response
        
        question = self.generator.generate_ai_question(5.0, "formulas")
        self.assertIsNotNone(question)
        self.assertEqual(question.category, "formulas")

class TestAnswerEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = AnswerEvaluator()
        self.sample_question = ExcelQuestion(
            question_id="test1",
            text="How to use VLOOKUP?",
            category="formulas",
            difficulty=5.0,
            expected_answer="VLOOKUP syntax...",
            evaluation_criteria=["accuracy", "clarity"]
        )

    def test_evaluate_response(self):
        """Test answer evaluation"""
        response = "VLOOKUP is used by..."
        evaluation = self.evaluator.evaluate_response(
            self.sample_question,
            response
        )
        self.assertIsInstance(evaluation, AnswerEvaluation)
        self.assertTrue(0 <= evaluation.technical_score <= 10)
        self.assertTrue(0 <= evaluation.overall_score <= 10)

    def test_fallback_evaluation(self):
        """Test fallback evaluation system"""
        self.evaluator.client = None  # Simulate AI service unavailable
        response = "Basic VLOOKUP answer"
        evaluation = self.evaluator.evaluate_response(
            self.sample_question,
            response
        )
        self.assertIsNotNone(evaluation)
        self.assertIsInstance(evaluation, AnswerEvaluation)

    @patch('google.generativeai.GenerativeModel')
    def test_ai_evaluation(self, mock_ai):
        """Test AI-powered evaluation"""
        mock_response = MagicMock()
        mock_response.text = {
            'technical_score': 8.5,
            'approach_score': 7.0,
            'communication_score': 8.0,
            'overall_score': 7.8,
            'feedback': 'Good answer',
            'strengths': ['Clear explanation'],
            'areas_for_improvement': ['Add examples']
        }
        mock_ai.return_value.generate_content.return_value = mock_response
        
        evaluation = self.evaluator.evaluate_response(
            self.sample_question,
            "Test answer"
        )
        self.assertIsNotNone(evaluation)
        self.assertEqual(evaluation.technical_score, 8.5)

if __name__ == '__main__':
    unittest.main()
