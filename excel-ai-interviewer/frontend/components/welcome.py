import streamlit as st
from src.models.interview import CandidateInfo

# Welcome component
class WelcomeComponent:
    def __init__(self):
        if 'form_submitted' not in st.session_state:
            st.session_state.form_submitted = False

    def render(self):
        """Render welcome screen"""
        st.title("📊 Excel Skills Interview")
        
        # Introduction
        st.markdown("""
        Welcome to the AI-powered Excel Skills Assessment! 
        This interview will evaluate your:
        - Technical Excel knowledge
        - Problem-solving approach
        - Communication skills
        
        Please fill in your details to begin.
        """)
        
        # Candidate registration form
        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", key="name")
                email = st.text_input("Email Address*", key="email")
                
            with col2:
                position = st.selectbox(
                    "Position Applied For*",
                    options=[
                        "Excel Analyst",
                        "Data Analyst",
                        "Financial Analyst",
                        "Business Analyst",
                        "Other"
                    ],
                    key="position"
                )
                
                experience = st.select_slider(
                    "Excel Experience Level*",
                    options=["Beginner", "Intermediate", "Advanced", "Expert"],
                    key="experience"
                )
            
            department = st.selectbox(
                "Department",
                options=[
                    "Finance",
                    "Operations",
                    "Analytics",
                    "Sales",
                    "Other"
                ],
                key="department"
            )
            
            # Optional information
            with st.expander("Additional Information (Optional)"):
                linkedin = st.text_input("LinkedIn Profile URL")
                referral = st.text_input("Referral Source")
            
            # Terms acceptance
            st.markdown("---")
            terms = st.checkbox(
                "I understand this is a mock interview for practice purposes",
                key="terms"
            )
            
            submitted = st.form_submit_button("Start Interview")
            
            if submitted and terms and name and email and position:
                candidate = CandidateInfo(
                    name=name,
                    email=email,
                    position_applied=position,
                    experience_level=experience,
                    department=department,
                    linkedin_profile=linkedin,
                    referral_source=referral
                )
                st.session_state.candidate = candidate
                st.session_state.form_submitted = True
                return True
            
            elif submitted:
                st.error("Please fill in all required fields (*) and accept the terms.")
                
        # Display interview tips
        with st.sidebar:
            st.write("### Interview Tips")
            st.info("""
            - Take your time to think before answering
            - Explain your thought process
            - Use specific examples when possible
            - Ask for clarification if needed
            """)
            
        return False
