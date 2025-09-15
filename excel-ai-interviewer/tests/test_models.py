# Tests for models

import unittest
from datetime import datetime
from src.models.question import ExcelQuestion
from src.models.evaluation import AnswerEvaluation
from src.models.interview import InterviewSession, CandidateInfo, InterviewStage, InterviewStatus

class TestModels(unittest.TestCase):
    def test_question_model(self):
        """Test ExcelQuestion model"""
        question = ExcelQuestion(
            question_id="q1",
            text="How do you use VLOOKUP?",
            category="formulas",
            difficulty=5.0,
            expected_answer="VLOOKUP syntax...",
            evaluation_criteria=["accuracy", "clarity"]
        )
        
        self.assertEqual(question.question_id, "q1")
        self.assertEqual(question.difficulty, 5.0)
        self.assertIn("accuracy", question.evaluation_criteria)
        
        # Test serialization
        question_dict = question.to_dict()
        self.assertIsInstance(question_dict, dict)
        self.assertEqual(question_dict["text"], "How do you use VLOOKUP?")

    def test_evaluation_model(self):
        """Test AnswerEvaluation model"""
        eval = AnswerEvaluation(
            technical_score=8.5,
            approach_score=7.0,
            communication_score=9.0,
            overall_score=8.2,
            feedback="Good explanation",
            strengths=["Clear communication"],
            areas_for_improvement=["Add examples"]
        )
        
        self.assertGreaterEqual(eval.technical_score, 0)
        self.assertLessEqual(eval.technical_score, 10)
        self.assertEqual(len(eval.strengths), 1)
        
        # Test serialization
        eval_dict = eval.to_dict()
        self.assertIsInstance(eval_dict, dict)
        self.assertEqual(eval_dict["overall_score"], 8.2)

    def test_interview_session(self):
        """Test InterviewSession model"""
        session = InterviewSession()
        
        # Test initial state
        self.assertEqual(session.stage, InterviewStage.WELCOME)
        self.assertEqual(session.status, InterviewStatus.IN_PROGRESS)
        
        # Test interview progression
        session.start_interview()
        self.assertEqual(session.stage, InterviewStage.QUESTIONING)
        self.assertIsNotNone(session.started_at)
        
        session.complete_interview()
        self.assertEqual(session.stage, InterviewStage.COMPLETE)
        self.assertEqual(session.status, InterviewStatus.COMPLETED)
        
        # Test duration calculation
        duration = session.get_duration_minutes()
        self.assertIsNotNone(duration)
        self.assertIsInstance(duration, float)

    def test_candidate_info(self):
        """Test CandidateInfo model"""
        candidate = CandidateInfo(
            name="John Doe",
            email="john@example.com",
            position_applied="Excel Analyst",
            experience_level="Intermediate",
            department="Finance"
        )
        
        self.assertEqual(candidate.name, "John Doe")
        self.assertEqual(candidate.experience_level, "Intermediate")
        
        # Test optional fields
        self.assertIsNone(candidate.linkedin_profile)
        self.assertIsNone(candidate.resume_summary)

if __name__ == '__main__':
    unittest.main()
