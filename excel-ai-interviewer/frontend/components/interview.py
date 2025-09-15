import streamlit as st
import time
from datetime import datetime
from src.models.interview import InterviewSession, InterviewStage, CandidateInfo
from src.services.question_generator import QuestionGenerator
from src.services.answer_evaluator import AnswerEvaluator

class InterviewComponent:
    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.answer_evaluator = AnswerEvaluator()
        
        # Initialize session state
        if 'interview' not in st.session_state:
            st.session_state.interview = InterviewSession()
        if 'current_question' not in st.session_state:
            st.session_state.current_question = None
            
    def render(self):
        """Render interview interface"""
        interview = st.session_state.interview
        
        if interview.stage == InterviewStage.WELCOME:
            self._render_welcome()
        elif interview.stage == InterviewStage.QUESTIONING:
            self._render_interview()
        elif interview.stage == InterviewStage.COMPLETE:
            self._render_summary()
            
    def _render_welcome(self):
        """Render welcome screen and candidate info form"""
        st.title("Excel Skills Interview")
        
        with st.form("candidate_info"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            position = st.selectbox(
                "Position Applied For",
                ["Excel Analyst", "Data Analyst", "Financial Analyst"]
            )
            experience = st.selectbox(
                "Experience Level",
                ["Beginner", "Intermediate", "Advanced"]
            )
            
            if st.form_submit_button("Start Interview"):
                candidate = CandidateInfo(
                    name=name,
                    email=email,
                    position_applied=position,
                    experience_level=experience
                )
                st.session_state.interview.candidate_info = candidate
                st.session_state.interview.start_interview()
                st.experimental_rerun()
                
    def _render_interview(self):
        """Render question and answer interface"""
        interview = st.session_state.interview
        
        # Display progress
        progress = interview.metrics.questions_answered / interview.metrics.total_questions
        st.progress(progress)
        
        # Get next question if needed
        if not st.session_state.current_question:
            question = self.question_generator.get_next_question(
                target_difficulty=interview.current_difficulty
            )
            if question:
                st.session_state.current_question = question
                interview.set_current_question(question)
            else:
                interview.complete_interview()
                st.experimental_rerun()
                return
                
        # Display current question
        st.write("### Question:")
        st.write(st.session_state.current_question.text)
        
        # Answer input
        with st.form("answer_form"):
            answer = st.text_area("Your Answer")
            start_time = time.time()
            
            if st.form_submit_button("Submit"):
                # Evaluate answer
                evaluation = self.answer_evaluator.evaluate_response(
                    st.session_state.current_question,
                    answer
                )
                
                # Record response
                interview.add_conversation_turn(
                    speaker="candidate",
                    message=answer,
                    response_time=time.time() - start_time,
                    evaluation=evaluation
                )
                
                # Clear current question and update UI
                st.session_state.current_question = None
                st.experimental_rerun()
                
    def _render_summary(self):
        """Render interview summary and feedback"""
        interview = st.session_state.interview
        
        st.title("Interview Complete")
        st.write(f"Duration: {interview.get_duration_minutes():.1f} minutes")
        
        # Display scores
        st.write("### Performance Scores")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Technical", f"{interview.metrics.avg_technical:.1f}/10")
        with col2:
            st.metric("Approach", f"{interview.metrics.avg_approach:.1f}/10")
        with col3:
            st.metric("Communication", f"{interview.metrics.avg_communication:.1f}/10")
            
        # Display strengths and improvements
        st.write("### Strengths")
        for strength in interview.strengths:
            st.write(f"- {strength}")
            
        st.write("### Areas for Improvement")
        for area in interview.areas_for_improvement:
            st.write(f"- {area}")
            
        # Restart option
        if st.button("Start New Interview"):
            st.session_state.interview = InterviewSession()
            st.session_state.current_question = None
            st.experimental_rerun()
