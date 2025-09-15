from typing import Dict, Any, List
from datetime import datetime
from src.models.interview import InterviewSession
from src.models.question import Question
from src.models.evaluation import InterviewResponse

class ReportGenerator:
    """Generates comprehensive interview performance reports"""
    
    def generate_final_report(self, session: InterviewSession) -> Dict[str, Any]:
        """Generate comprehensive interview report"""
        
        if not session.responses:
            return {"error": "No responses to evaluate"}
        
        # Basic metrics
        basic_metrics = self._calculate_basic_metrics(session)
        
        # Performance analysis
        performance_analysis = self._analyze_performance(session)
        
        # Category breakdown
        category_performance = self._analyze_category_performance(session)
        
        # Skill assessment
        skill_assessment = self._assess_skill_level(session)
        
        # Recommendations
        recommendations = self._generate_recommendations(session, skill_assessment)
        
        # Detailed question review
        question_details = self._create_question_details(session)
        
        return {
            "session_info": {
                "candidate_name": session.candidate_name,
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else datetime.now().isoformat(),
                "duration_minutes": session.get_duration_minutes()
            },
            "basic_metrics": basic_metrics,
            "performance_analysis": performance_analysis,
            "category_performance": category_performance,
            "skill_assessment": skill_assessment,
            "recommendations": recommendations,
            "question_details": question_details
        }
    
    def _calculate_basic_metrics(self, session: InterviewSession) -> Dict[str, Any]:
        """Calculate basic interview metrics"""
        scores = [r.evaluation_score for r in session.responses]
        difficulties = [q.difficulty for q in session.questions_asked]
        
        return {
            "total_questions": len(session.questions_asked),
            "overall_score": session.get_average_score(),
            "score_range": f"{min(scores):.1f} - {max(scores):.1f}",
            "difficulty_range": f"{min(difficulties):.1f} - {max(difficulties):.1f}",
            "average_difficulty": sum(difficulties) / len(difficulties) if difficulties else 0
        }
    
    def _analyze_performance(self, session: InterviewSession) -> Dict[str, Any]:
        """Analyze performance trends and patterns"""
        scores = [r.evaluation_score for r in session.responses]
        
        # Performance trend
        if len(scores) > 1:
            trend = "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
        else:
            trend = "single_question"
        
        # Consistency analysis
        score_variance = self._calculate_variance(scores)
        consistency = "high" if score_variance < 2 else "medium" if score_variance < 4 else "low"
        
        # Speed analysis
        response_times = [getattr(r, 'response_time_seconds', 60) for r in session.responses]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 60
        
        return {
            "trend": trend,
            "consistency": consistency,
            "score_variance": score_variance,
            "average_response_time": avg_response_time,
            "fastest_response": min(response_times) if response_times else 0,
            "slowest_response": max(response_times) if response_times else 0
        }
    
    def _analyze_category_performance(self, session: InterviewSession) -> Dict[str, Any]:
        """Analyze performance by Excel skill category"""
        category_scores = {}
        
        for question, response in zip(session.questions_asked, session.responses):
            category = question.category
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(response.evaluation_score)
        
        category_summary = {}
        for category, scores in category_scores.items():
            category_summary[category] = {
                "average_score": sum(scores) / len(scores),
                "questions_count": len(scores),
                "best_score": max(scores),
                "category_display": category.replace('_', ' ').title()
            }
        
        # Identify strongest and weakest categories
        if category_summary:
            strongest = max(category_summary.keys(), key=lambda x: category_summary[x]["average_score"])
            weakest = min(category_summary.keys(), key=lambda x: category_summary[x]["average_score"])
        else:
            strongest = weakest = None
        
        return {
            "categories": category_summary,
            "strongest_category": strongest,
            "weakest_category": weakest
        }
    
    def _assess_skill_level(self, session: InterviewSession) -> Dict[str, Any]:
        """Assess overall Excel skill level"""
        avg_score = session.get_average_score()
        max_difficulty = max(q.difficulty for q in session.questions_asked) if session.questions_asked else 0
        
        # Determine skill level based on score and difficulty handled
        if avg_score >= 8 and max_difficulty >= 7:
            level = "Expert"
            description = "Advanced Excel user with deep knowledge across multiple areas"
        elif avg_score >= 6 and max_difficulty >= 5:
            level = "Advanced"
            description = "Strong Excel skills suitable for most analytical roles"
        elif avg_score >= 4 and max_difficulty >= 3:
            level = "Intermediate"
            description = "Good foundational Excel skills with room for growth"
        else:
            level = "Beginner"
            description = "Basic Excel knowledge requiring significant development"
        
        # Hiring recommendation
        if avg_score >= 7:
            hiring_rec = "Strong Recommend"
        elif avg_score >= 5:
            hiring_rec = "Recommend with Training"
        elif avg_score >= 3:
            hiring_rec = "Consider for Junior Roles"
        else:
            hiring_rec = "Not Recommended"
        
        return {
            "skill_level": level,
            "description": description,
            "hiring_recommendation": hiring_rec,
            "confidence_score": min(100, max(0, (avg_score / 10) * 100))
        }
    
    def _generate_recommendations(self, session: InterviewSession, skill_assessment: Dict) -> Dict[str, List[str]]:
        """Generate specific recommendations based on performance"""
        strengths = []
        improvements = []
        training_suggestions = []
        
        avg_score = session.get_average_score()
        
        # Analyze category performance for specific recommendations
        category_scores = {}
        for question, response in zip(session.questions_asked, session.responses):
            category = question.category
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(response.evaluation_score)
        
        # Generate category-specific recommendations
        for category, scores in category_scores.items():
            avg_cat_score = sum(scores) / len(scores)
            category_name = category.replace('_', ' ').title()
            
            if avg_cat_score >= 7:
                strengths.append(f"Strong performance in {category_name}")
            elif avg_cat_score <= 4:
                improvements.append(f"Needs improvement in {category_name}")
                training_suggestions.extend(self._get_category_training(category))
        
        # General recommendations based on overall performance
        if avg_score >= 7:
            strengths.append("Demonstrates solid Excel expertise")
            training_suggestions.append("Consider advanced Excel certification")
        elif avg_score >= 5:
            improvements.append("Focus on consistency across all Excel areas")
            training_suggestions.extend([
                "Practice with real-world Excel scenarios",
                "Review intermediate Excel functions"
            ])
        else:
            improvements.append("Requires comprehensive Excel training")
            training_suggestions.extend([
                "Complete basic Excel fundamentals course",
                "Practice with guided Excel tutorials"
            ])
        
        return {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "training_suggestions": training_suggestions
        }
    
    def _get_category_training(self, category: str) -> List[str]:
        """Get training suggestions for specific categories"""
        training_map = {
            "basic_formulas": [
                "Practice basic Excel functions (SUM, AVERAGE, COUNT)",
                "Learn about absolute vs relative cell references"
            ],
            "data_analysis": [
                "Master VLOOKUP and INDEX/MATCH functions",
                "Learn pivot table creation and analysis"
            ],
            "advanced_functions": [
                "Study array formulas and advanced functions",
                "Practice with conditional formatting and data validation"
            ],
            "automation": [
                "Learn VBA basics for Excel automation",
                "Explore Power Query for data transformation"
            ]
        }
        return training_map.get(category, ["Focus on this Excel skill area"])
    
    def _create_question_details(self, session: InterviewSession) -> List[Dict[str, Any]]:
        """Create detailed breakdown of each question and response"""
        details = []
        
        for i, (question, response) in enumerate(zip(session.questions_asked, session.responses)):
            detail = {
                "question_number": i + 1,
                "question_text": question.text,
                "category": question.get_category_display(),
                "difficulty": question.difficulty,
                "difficulty_level": question.get_difficulty_level(),
                "candidate_response": response.response,
                "score": response.evaluation_score,
                "performance_level": response.get_performance_level(),
                "feedback": response.feedback,
                "response_time": getattr(response, 'response_time_seconds', 0)
            }
            details.append(detail)
        
        return details
    
    def _calculate_variance(self, scores: List[float]) -> float:
        """Calculate variance of scores"""
        if len(scores) <= 1:
            return 0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance
    
    def generate_summary_report(self, session: InterviewSession) -> str:
        """Generate a concise text summary of the interview"""
        full_report = self.generate_final_report(session)
        
        summary_parts = [
            f"Excel Interview Summary for {session.candidate_name}",
            f"Overall Score: {full_report['basic_metrics']['overall_score']:.1f}/10",
            f"Skill Level: {full_report['skill_assessment']['skill_level']}",
            f"Recommendation: {full_report['skill_assessment']['hiring_recommendation']}"
        ]
        
        if full_report['category_performance']['strongest_category']:
            strongest = full_report['category_performance']['strongest_category']
            summary_parts.append(f"Strongest Area: {strongest.replace('_', ' ').title()}")
        
        if full_report['category_performance']['weakest_category']:
            weakest = full_report['category_performance']['weakest_category']
            summary_parts.append(f"Development Area: {weakest.replace('_', ' ').title()}")
        
        return " | ".join(summary_parts)