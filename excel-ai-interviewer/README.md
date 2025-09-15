# 📊 Excel AI Interviewer

**Excel AI Interviewer** is an AI-powered mock interview tool that helps you practice Excel interview questions in a real-time interactive environment.  
It combines Python, Streamlit, and AI models to simulate interviewer-candidate sessions.

---

## 🌐 Live Demo

👉 Try it here: [Excel AI Interviewer](https://aimockexcelinterviewer.streamlit.app/)

---

## 🚀 Features

- 🧠 **AI-driven Q&A** – Generate Excel-related interview questions dynamically.  
- 🎤 **Mock Interview Simulation** – Practice answering in a realistic flow.  
- 🎨 **Interactive UI** – Clean and simple frontend built with Streamlit.  
- ⚙️ **Modular Design** – Separate frontend and backend code for easy extension.  
- ☁️ **Deployed Online** – Access from any device via Streamlit Cloud.  

---

## 📂 Project Structure
excel-ai-interviewer/
├── README.md
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── interview.py
│   │   ├── question.py
│   │   └── evaluation.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── difficulty_manager.py
│   │   ├── answer_evaluator.py
│   │   ├── question_generator.py
│   │   └── report_generator.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── question_bank.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── helpers.py
├── frontend/
│   ├── __init__.py
│   ├── main.py              # <--- Entry point for Streamlit Cloud
│   ├── components/
│   │   ├── __init__.py
│   │   ├── welcome.py
│   │   ├── interview.py
│   │   └── results.py
│   └── styles/
│       └── custom.css
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_integration.py
└── .streamlit/
    ├── config.toml          # Streamlit theme/config
    └── secrets.toml         # (optional) for API keys, DB creds

