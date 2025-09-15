import streamlit as st
import pandas as pd
import plotly.express as px
from src.models.interview import InterviewSession

class ResultsComponent:
    def __init__(self, interview: InterviewSession):
        self.interview = interview
        
    def render(self):
        """Render results dashboard"""
        st.title("Interview Results")
        
        # Candidate info
        self._render_candidate_info()
        
        # Score summary
        self._render_score_summary()
        
        # Detailed analytics
        self._render_analytics()
        
        # Export options
        self._render_export_options()
        
    def _render_candidate_info(self):
        """Display candidate information"""
        candidate = self.interview.candidate_info
        if not candidate:
            return
            
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Candidate Details")
            st.write(f"**Name:** {candidate.name}")
            st.write(f"**Position:** {candidate.position_applied}")
            st.write(f"**Experience:** {candidate.experience_level}")
        with col2:
            st.write("### Interview Summary")
            st.write(f"**Duration:** {self.interview.get_duration_minutes():.1f} minutes")
            st.write(f"**Questions:** {self.interview.metrics.questions_answered}")
            st.write(f"**Completion:** {self.interview.get_completion_rate():.1f}%")
    
    def _render_score_summary(self):
        """Display score summary with charts"""
        st.write("### Performance Scores")
        
        # Radar chart of scores
        scores = {
            'Technical': self.interview.metrics.avg_technical,
            'Approach': self.interview.metrics.avg_approach,
            'Communication': self.interview.metrics.avg_communication
        }
        
        df = pd.DataFrame(dict(
            r=list(scores.values()),
            theta=list(scores.keys())
        ))
        
        fig = px.line_polar(df, r='r', theta='theta', line_close=True,
                           range_r=[0,10], title="Skills Assessment")
        st.plotly_chart(fig)
        
        # Overall recommendation
        st.write("### Overall Assessment")
        st.write(self.interview.final_recommendation)
        st.metric("Confidence Score", f"{self.interview.confidence_score:.1f}%")
    
    def _render_analytics(self):
        """Display detailed analytics"""
        st.write("### Detailed Analytics")
        
        # Question difficulty progression
        difficulties = pd.DataFrame({
            'Question': range(1, len(self.interview.metrics.difficulty_progression) + 1),
            'Difficulty': self.interview.metrics.difficulty_progression
        })
        
        fig = px.line(difficulties, x='Question', y='Difficulty',
                     title="Question Difficulty Progression")
        st.plotly_chart(fig)
        
        # Response time analysis
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Response Time", 
                     f"{self.interview.metrics.avg_response_time:.1f}s")
        
        # Category coverage
        coverage = self.interview.metrics.get_category_coverage()
        coverage_df = pd.DataFrame(coverage).T
        st.write("### Category Coverage")
        st.dataframe(coverage_df)
    
    def _render_export_options(self):
        """Provide export options"""
        st.write("### Export Results")
        
        if st.button("Download Detailed Report"):
            report = self._generate_report()
            st.download_button(
                "Download Report",
                report,
                file_name=f"interview_report_{self.interview.session_id}.txt",
                mime="text/plain"
            )
    
    def _generate_report(self) -> str:
        """Generate detailed text report"""
        report = []
        report.append("EXCEL INTERVIEW ASSESSMENT REPORT")
        report.append("-" * 40)
        
        # Add candidate info
        if self.interview.candidate_info:
            report.append(f"Candidate: {self.interview.candidate_info.name}")
            report.append(f"Position: {self.interview.candidate_info.position_applied}")
            report.append(f"Experience: {self.interview.candidate_info.experience_level}")
        
        # Add scores
        report.append("\nSCORES")
        report.append(f"Technical: {self.interview.metrics.avg_technical:.1f}/10")
        report.append(f"Approach: {self.interview.metrics.avg_approach:.1f}/10")
        report.append(f"Communication: {self.interview.metrics.avg_communication:.1f}/10")
        
        # Add strengths and improvements
        report.append("\nSTRENGTHS")
        for strength in self.interview.strengths:
            report.append(f"- {strength}")
            
        report.append("\nAREAS FOR IMPROVEMENT")
        for area in self.interview.areas_for_improvement:
            report.append(f"- {area}")
            
        return "\n".join(report)
