# 🧠 AI-Personalized-Learning-Platform

An **AI-powered personalized learning platform** that allows users to upload documents (PDF, PPT, DOC), extract key concepts using **Large Language Models (LLMs)** like **Ollama**, auto-generate quizzes (MCQs, True/False, Fill in the Blanks), and receive performance feedback.

Built using **Flutter** for the frontend and **Flask + Python** for the backend — offering a seamless, interactive, and intelligent learning experience.

---

## 🚀 Features

- 📤 Upload educational files (PDF, PPT, DOCX)
- 🔍 Extract key concepts using Ollama LLM
- 🧠 AI-generated quizzes (MCQ, True/False, Fill in the Blank)
- 📸 Upload and manage profile pictures
- 📊 Get automatic evaluation with grades and score
- 🎯 Personalized learning feedback
- 🧩 Modular Flask backend for extensibility

---

## 🧠 Quiz Generation Logic

1. **File Upload**: Users upload PDF, PPT, or DOC files.
2. **Text Extraction**: File content is parsed and cleaned.
3. **Concept Extraction**: Text is sent to Ollama's local LLM for identifying key concepts.
4. **Question Generation**: 
   - 2 MCQs
   - 2 True/False
   - 1 Fill in the Blank
5. **Answer Evaluation**: Responses are graded, and feedback is given in real-time.

---

## 🛠️ Tech Stack

| Layer       | Tech Used                      |
|-------------|-------------------------------|
| **Frontend** |  HTML/CSS                     |
| **Backend**  | Flask (Python)                |
| **AI**       | Ollama (Local LLM)            |
| **Database** | SQLite + SQLAlchemy ORM       |
| **Forms**    | Flask-WTF                     |
| **Deployment** | Render / Railway / Local    |

---

## Our Team
Malak Soni (Backend,AI)
Hetvi Patel (Frontend , AI)

