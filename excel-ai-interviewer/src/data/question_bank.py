from typing import List, Optional
from src.models.question import Question

class QuestionBank:
    """Manages the pool of Excel interview questions"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
    
    def _initialize_questions(self) -> List[Question]:
        """Initialize with hardcoded questions for POC"""
        return [
            # Basic Formulas (Difficulty 1-4)
            Question(
                id="basic_1",
                text="How would you calculate the sum of values in cells A1 to A10? Please write the exact formula.",
                category="basic_formulas",
                difficulty=2.0,
                expected_answer="=SUM(A1:A10)",
                evaluation_criteria=["correct_function", "proper_range", "syntax"]
            ),
            Question(
                id="basic_2", 
                text="What's the difference between absolute and relative cell references? Give an example of each.",
                category="basic_formulas",
                difficulty=3.0,
                expected_answer="Relative: A1 changes when copied. Absolute: $A$1 stays fixed when copied.",
                evaluation_criteria=["understands_concept", "provides_examples", "syntax_knowledge"]
            ),
            Question(
                id="basic_3",
                text="How would you calculate the average of numbers in column B, excluding blank cells?",
                category="basic_formulas",
                difficulty=2.5,
                expected_answer="=AVERAGE(B:B) or =AVERAGEA(B:B)",
                evaluation_criteria=["correct_function", "handles_blanks", "range_specification"]
            ),
            Question(
                id="basic_4",
                text="What function would you use to count non-empty cells in a range? Write an example.",
                category="basic_formulas",
                difficulty=2.0,
                expected_answer="=COUNTA(A1:A10) counts non-empty cells",
                evaluation_criteria=["correct_function", "understands_difference", "syntax"]
            ),
            
            # Data Analysis (Difficulty 4-7)
            Question(
                id="data_1",
                text="You have sales data in column A and dates in column B. How would you find the total sales for a specific month?",
                category="data_analysis", 
                difficulty=5.0,
                expected_answer="Use SUMIFS function: =SUMIFS(A:A, B:B, \">=\"&DATE(year,month,1), B:B, \"<\"&DATE(year,month+1,1))",
                evaluation_criteria=["appropriate_function", "date_handling", "criteria_logic"]
            ),
            Question(
                id="data_2",
                text="Explain the difference between VLOOKUP and INDEX/MATCH. When would you use each?",
                category="data_analysis",
                difficulty=6.0,
                expected_answer="VLOOKUP searches right, limited. INDEX/MATCH more flexible, can search left, better performance.",
                evaluation_criteria=["understands_limitations", "performance_awareness", "use_cases"]
            ),
            Question(
                id="data_3",
                text="How would you create a pivot table to analyze sales by region and product category?",
                category="data_analysis",
                difficulty=5.5,
                expected_answer="Insert > Pivot Table, drag Region to Rows, Product Category to Columns, Sales to Values",
                evaluation_criteria=["pivot_knowledge", "field_placement", "analysis_thinking"]
            ),
            Question(
                id="data_4",
                text="What's the best way to remove duplicate entries from a large dataset in Excel?",
                category="data_analysis",
                difficulty=4.5,
                expected_answer="Data tab > Remove Duplicates, or Advanced Filter with unique records only",
                evaluation_criteria=["knows_tools", "data_cleaning", "best_practices"]
            ),
            
            # Advanced Functions (Difficulty 6-9)
            Question(
                id="advanced_1",
                text="How would you create a dynamic dropdown list that updates based on another cell's value?",
                category="advanced_functions",
                difficulty=8.0,
                expected_answer="Use INDIRECT function with named ranges or OFFSET function with data validation.",
                evaluation_criteria=["advanced_functions", "data_validation", "dynamic_references"]
            ),
            Question(
                id="advanced_2",
                text="Write a formula to find the second highest value in a range A1:A100.",
                category="advanced_functions",
                difficulty=7.0,
                expected_answer="=LARGE(A1:A100,2) or use array formula with LARGE function",
                evaluation_criteria=["statistical_functions", "ranking_knowledge", "formula_construction"]
            ),
            Question(
                id="advanced_3",
                text="How would you use array formulas to perform calculations across multiple ranges simultaneously?",
                category="advanced_functions",
                difficulty=8.5,
                expected_answer="Use Ctrl+Shift+Enter for array formulas, can calculate multiple conditions or ranges at once",
                evaluation_criteria=["array_understanding", "complex_calculations", "efficiency"]
            ),
            Question(
                id="advanced_4",
                text="Explain how to use the CHOOSE function with a practical example.",
                category="advanced_functions",
                difficulty=6.5,
                expected_answer="CHOOSE(index_num, value1, value2, ...) returns value based on index. Example: =CHOOSE(2,\"Red\",\"Blue\",\"Green\") returns \"Blue\"",
                evaluation_criteria=["function_understanding", "practical_application", "syntax_knowledge"]
            ),
            
            # Automation & VBA (Difficulty 7-10)
            Question(
                id="automation_1",
                text="Describe how you would automate a monthly report generation process in Excel.",
                category="automation",
                difficulty=9.0,
                expected_answer="Use VBA macros, Power Query for data refresh, pivot tables, scheduled tasks.",
                evaluation_criteria=["automation_knowledge", "vba_understanding", "process_thinking"]
            ),
            Question(
                id="automation_2",
                text="What's the difference between recording a macro and writing VBA code manually?",
                category="automation",
                difficulty=7.5,
                expected_answer="Recorded macros capture exact steps, manual VBA allows logic, loops, conditions, more flexible",
                evaluation_criteria=["macro_understanding", "vba_knowledge", "flexibility_concepts"]
            ),
            Question(
                id="automation_3",
                text="How would you create a user form in Excel to collect data input?",
                category="automation",
                difficulty=8.5,
                expected_answer="VBA Editor > Insert UserForm, add controls, write VBA code for events and data handling",
                evaluation_criteria=["userform_knowledge", "vba_skills", "ui_design"]
            ),
            Question(
                id="automation_4",
                text="Explain how to use Excel's Power Query to import and transform data from multiple sources.",
                category="automation",
                difficulty=8.0,
                expected_answer="Data > Get Data, connect to sources, use Power Query Editor for transformations, load to worksheet",
                evaluation_criteria=["power_query_knowledge", "data_transformation", "modern_excel_features"]
            )
        ]
    
    def get_question_by_difficulty(self, target_difficulty: float, category: str = None, 
                                 exclude_ids: List[str] = None) -> Optional[Question]:
        """Get a question matching the target difficulty level and category"""
        exclude_ids = exclude_ids or []
        suitable_questions = []
        
        for q in self.questions:
            if q.id in exclude_ids:
                continue
                
            difficulty_match = abs(q.difficulty - target_difficulty) <= 2.0
            category_match = category is None or q.category == category
            
            if difficulty_match and category_match:
                suitable_questions.append(q)
        
        if not suitable_questions:
            # Fallback to closest difficulty in category
            category_questions = [q for q in self.questions 
                                if q.id not in exclude_ids and (category is None or q.category == category)]
            if category_questions:
                suitable_questions = sorted(category_questions, 
                                          key=lambda x: abs(x.difficulty - target_difficulty))
        
        return suitable_questions[0] if suitable_questions else None
    
    def get_questions_by_category(self, category: str) -> List[Question]:
        """Get all questions in a specific category"""
        return [q for q in self.questions if q.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all available question categories"""
        return list(set(q.category for q in self.questions))
    
    def get_difficulty_range(self, category: str = None) -> tuple:
        """Get min and max difficulty for category or all questions"""
        questions = self.questions if category is None else self.get_questions_by_category(category)
        if not questions:
            return (0, 0)
        difficulties = [q.difficulty for q in questions]
        return (min(difficulties), max(difficulties))
    
    def get_question_count(self, category: str = None) -> int:
        """Get total number of questions in category or all"""
        if category is None:
            return len(self.questions)
        return len(self.get_questions_by_category(category))
    
    def add_question(self, question: Question):
        """Add a new question to the bank"""
        # Check for duplicate IDs
        if any(q.id == question.id for q in self.questions):
            raise ValueError(f"Question with ID {question.id} already exists")
        self.questions.append(question)
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get a specific question by ID"""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None