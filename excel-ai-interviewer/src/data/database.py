import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from config.settings import settings
from src.models.interview import InterviewSession
from src.models.question import Question
from src.models.evaluation import InterviewResponse

class DatabaseManager:
    """Manages database operations for interview sessions"""
    
    def __init__(self, db_path: str = "excel_interviewer.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Interview sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interview_sessions (
                    session_id TEXT PRIMARY KEY,
                    candidate_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    current_difficulty REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Questions asked table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions_asked (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty REAL NOT NULL,
                    expected_answer TEXT NOT NULL,
                    evaluation_criteria TEXT NOT NULL,
                    asked_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
                )
            ''')
            
            # Responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    evaluation_score REAL NOT NULL,
                    technical_score REAL DEFAULT 0,
                    approach_score REAL DEFAULT 0,
                    communication_score REAL DEFAULT 0,
                    feedback TEXT NOT NULL,
                    response_time_seconds REAL DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
                )
            ''')
            
            # Analytics table for performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interview_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    skill_level TEXT NOT NULL,
                    hiring_recommendation TEXT NOT NULL,
                    strongest_category TEXT,
                    weakest_category TEXT,
                    total_questions INTEGER NOT NULL,
                    interview_duration_minutes REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
                )
            ''')
            
            conn.commit()
    
    def save_interview_session(self, session: InterviewSession) -> bool:
        """Save or update an interview session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or update session
                cursor.execute('''
                    INSERT OR REPLACE INTO interview_sessions 
                    (session_id, candidate_name, start_time, end_time, current_difficulty, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session.session_id,
                    session.candidate_name,
                    session.start_time.isoformat(),
                    session.end_time.isoformat() if session.end_time else None,
                    session.current_difficulty,
                    session.status,
                    datetime.now().isoformat()
                ))
                
                # Save questions asked
                for question in session.questions_asked:
                    cursor.execute('''
                        INSERT OR REPLACE INTO questions_asked 
                        (session_id, question_id, question_text, category, difficulty, 
                         expected_answer, evaluation_criteria, asked_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session.session_id,
                        question.id,
                        question.text,
                        question.category,
                        question.difficulty,
                        question.expected_answer,
                        json.dumps(question.evaluation_criteria),
                        datetime.now().isoformat()
                    ))
                
                # Save responses
                for response in session.responses:
                    cursor.execute('''
                        INSERT OR REPLACE INTO responses 
                        (session_id, question_id, response_text, timestamp, evaluation_score,
                         technical_score, approach_score, communication_score, feedback, response_time_seconds)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session.session_id,
                        response.question_id,
                        response.response,
                        response.timestamp.isoformat(),
                        response.evaluation_score,
                        getattr(response, 'technical_score', 0),
                        getattr(response, 'approach_score', 0),
                        getattr(response, 'communication_score', 0),
                        response.feedback,
                        getattr(response, 'response_time_seconds', 0)
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving interview session: {e}")
            return False
    
    def load_interview_session(self, session_id: str) -> Optional[InterviewSession]:
        """Load an interview session from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Load session data
                cursor.execute('''
                    SELECT session_id, candidate_name, start_time, end_time, current_difficulty, status
                    FROM interview_sessions WHERE session_id = ?
                ''', (session_id,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    return None
                
                # Create session object
                session = InterviewSession(
                    session_id=session_data[0],
                    candidate_name=session_data[1],
                    start_time=datetime.fromisoformat(session_data[2]),
                    current_difficulty=session_data[4],
                    status=session_data[5]
                )
                
                if session_data[3]:  # end_time
                    session.end_time = datetime.fromisoformat(session_data[3])
                
                # Load questions
                cursor.execute('''
                    SELECT question_id, question_text, category, difficulty, expected_answer, evaluation_criteria
                    FROM questions_asked WHERE session_id = ? ORDER BY asked_at
                ''', (session_id,))
                
                for q_data in cursor.fetchall():
                    question = Question(
                        id=q_data[0],
                        text=q_data[1],
                        category=q_data[2],
                        difficulty=q_data[3],
                        expected_answer=q_data[4],
                        evaluation_criteria=json.loads(q_data[5])
                    )
                    session.questions_asked.append(question)
                
                # Load responses
                cursor.execute('''
                    SELECT question_id, response_text, timestamp, evaluation_score, 
                           technical_score, approach_score, communication_score, feedback, response_time_seconds
                    FROM responses WHERE session_id = ? ORDER BY timestamp
                ''', (session_id,))
                
                for r_data in cursor.fetchall():
                    response = InterviewResponse(
                        question_id=r_data[0],
                        response=r_data[1],
                        timestamp=datetime.fromisoformat(r_data[2]),
                        evaluation_score=r_data[3],
                        feedback=r_data[7]
                    )
                    response.technical_score = r_data[4]
                    response.approach_score = r_data[5]
                    response.communication_score = r_data[6]
                    response.response_time_seconds = r_data[8]
                    session.responses.append(response)
                
                return session
                
        except Exception as e:
            print(f"Error loading interview session: {e}")
            return None
    
    def save_analytics(self, session_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Save interview analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO interview_analytics 
                    (session_id, overall_score, skill_level, hiring_recommendation,
                     strongest_category, weakest_category, total_questions, interview_duration_minutes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    analytics_data.get('overall_score', 0),
                    analytics_data.get('skill_level', ''),
                    analytics_data.get('hiring_recommendation', ''),
                    analytics_data.get('strongest_category'),
                    analytics_data.get('weakest_category'),
                    analytics_data.get('total_questions', 0),
                    analytics_data.get('interview_duration_minutes', 0),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving analytics: {e}")
            return False
    
    def get_interview_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent interview history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT s.session_id, s.candidate_name, s.start_time, s.end_time, s.status,
                           a.overall_score, a.skill_level, a.hiring_recommendation, a.total_questions
                    FROM interview_sessions s
                    LEFT JOIN interview_analytics a ON s.session_id = a.session_id
                    ORDER BY s.start_time DESC
                    LIMIT ?
                ''', (limit,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'session_id': row[0],
                        'candidate_name': row[1],
                        'start_time': row[2],
                        'end_time': row[3],
                        'status': row[4],
                        'overall_score': row[5],
                        'skill_level': row[6],
                        'hiring_recommendation': row[7],
                        'total_questions': row[8]
                    })
                
                return history
                
        except Exception as e:
            print(f"Error getting interview history: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic stats
                cursor.execute('SELECT COUNT(*) FROM interview_sessions')
                total_interviews = cursor.fetchone()[0]
                
                cursor.execute('SELECT AVG(overall_score) FROM interview_analytics')
                avg_score = cursor.fetchone()[0] or 0
                
                cursor.execute('''
                    SELECT skill_level, COUNT(*) 
                    FROM interview_analytics 
                    GROUP BY skill_level
                ''')
                skill_distribution = dict(cursor.fetchall())
                
                cursor.execute('''
                    SELECT hiring_recommendation, COUNT(*) 
                    FROM interview_analytics 
                    GROUP BY hiring_recommendation
                ''')
                recommendation_distribution = dict(cursor.fetchall())
                
                return {
                    'total_interviews': total_interviews,
                    'average_score': avg_score,
                    'skill_distribution': skill_distribution,
                    'recommendation_distribution': recommendation_distribution
                }
                
        except Exception as e:
            print(f"Error getting performance stats: {e}")
            return {}