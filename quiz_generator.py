import json
import logging
import random
from flask import Flask, request, jsonify
import ollama

# ✅ Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Function: Generate Quiz Questions
import json
import re
import logging
import random
from flask import Flask, request, jsonify
import ollama

def extract_json(text):
    """Extracts valid JSON from a mixed text response using regex."""
    match = re.search(r'\{.*\}', text, re.DOTALL)  # Find JSON content
    if match:
        return match.group(0)  # Return the JSON part
    return None  # No JSON found

def generate_quiz(concepts, difficulty="medium"):
    if not concepts:
        logging.error("❌ No concepts provided for quiz generation")
        return {"error": "❌ No concepts provided"}

    quiz = []
    question_types = ["MCQ", "True/False", "Fill in the Blank"]

    for concept in concepts:
        # ✅ Handle both string and dictionary formats
        if isinstance(concept, str):
            concept_name = concept  
            concept_type = "General"
        elif isinstance(concept, dict):
            concept_name = concept.get("name", "Unknown Concept")
            concept_type = concept.get("type", "General")
        else:
            logging.error(f"❌ Invalid concept format: {concept}")
            continue

        question_type = random.choice(question_types)

        # ✅ Force JSON format strictly
        prompt = f"""
        You are a quiz generator. Create a **{question_type}** question for the concept "{concept_name}" ({concept_type}) with {difficulty} difficulty.
        - If MCQ, provide exactly **four** answer choices.
        - Always return a response in strict JSON format.
        
        Response Format:
        {{
          "question": "Write a question about {concept_name}.",
          "type": "{question_type}",
          "choices": ["Option A", "Option B", "Option C", "Option D"] if "{question_type}" == "MCQ" else [],
          "correct_answer": "Option B" if "{question_type}" == "MCQ" else "True" if "{question_type}" == "True/False" else "Correct answer text",
          "explanation": "A short explanation about why the answer is correct."
        }}
        """

        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
            raw_response = response["message"]["content"].strip()

            # ✅ Directly parse JSON (skip regex parsing)
            question_data = json.loads(raw_response)

            # ✅ Validate JSON format
            if not isinstance(question_data, dict) or "question" not in question_data or "correct_answer" not in question_data:
                logging.error(f"❌ Invalid AI-generated question format: {question_data}")
                quiz.append({"error": "❌ AI generated an invalid question", "concept": concept_name})
                continue

            # ✅ Ensure choices exist for MCQs
            if question_type == "MCQ" and (not isinstance(question_data.get("choices"), list) or len(question_data["choices"]) != 4):
                logging.error(f"❌ MCQ question missing proper options: {question_data}")
                quiz.append({"error": "❌ MCQ options were not properly generated", "concept": concept_name})
                continue

            question_data["difficulty"] = difficulty
            quiz.append(question_data)

        except json.JSONDecodeError:
            logging.error(f"❌ Failed to parse JSON from Ollama response: {raw_response}")
            quiz.append({"error": "❌ AI response contained invalid JSON", "concept": concept_name})

        except Exception as e:
            logging.error(f"❌ ERROR in generate_quiz: {e}")
            quiz.append({"error": "❌ Failed to generate question", "concept": concept_name})

    return quiz




# ✅ API Endpoint: Generate Quiz
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz_api():
    try:
        data = request.get_json(force=True, silent=True)
        logging.info(f"📩 Received Request: {data}")

        if not data or "concepts" not in data:
            return jsonify({"error": "❌ 'concepts' field is required"}), 400
        
        concepts = data.get("concepts", [])
        difficulty = data.get("difficulty", "medium")

        if not isinstance(concepts, list) or not concepts:
            logging.error("❌ 'concepts' should be a non-empty list")
            return jsonify({"error": "❌ 'concepts' should be a non-empty list"}), 400

        logging.info(f"📚 Generating quiz for concepts: {concepts} with {difficulty} difficulty")
        quiz = generate_quiz(concepts, difficulty)

        logging.info(f"✅ Generated Quiz: {quiz}")  # ✅ Log response for debugging
        return jsonify({"quiz": quiz})

    except Exception as e:
        logging.error(f"❌ Error in /generate_quiz: {str(e)}")
        return jsonify({"error": f"❌ Server Error: {str(e)}"}), 500

# ✅ Function: Evaluate Answers
def evaluate_answers(quiz, user_answers):
    if not quiz or not user_answers:
        return {"error": "❌ Quiz or answers missing"}

    evaluation = []
    for i, question in enumerate(quiz):
        correct_answer = question.get("correct_answer", "").strip()
        user_response = user_answers[i].strip() if i < len(user_answers) else ""

        # Check if user answer is empty
        if not user_response:
            evaluation.append({
                "score": 0,
                "feedback": "You did not provide an answer.",
                "suggestions": "Please make sure to answer all questions."
            })
            continue

        prompt = f"""
        Question: "{question['question']}"
        Correct Answer: "{correct_answer}"
        User Answer: "{user_response}"

        Evaluate and provide:
        - Score (0-10)
        - Explanation
        - Improvement tips

        Respond in JSON format:
        {{
          "score": 8,
          "feedback": "Your explanation",
          "suggestions": "How to improve?"
        }}
        """

        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
            raw_response = response["message"]["content"].strip()

            # Validate the response format
            try:
                evaluation.append(json.loads(raw_response))
            except json.JSONDecodeError:
                evaluation.append({
                    "score": 0,
                    "feedback": "Failed to parse model response.",
                    "suggestions": "Try rephrasing your answer or check your input."
                })

        except Exception as e:
            logging.error(f"❌ ERROR in evaluate_answers: {e}")
            evaluation.append({
                "score": 0,
                "feedback": "Error in evaluation process.",
                "suggestions": "There was an issue evaluating your answer."
            })

    return evaluation


# ✅ API Endpoint: Evaluate Answers
@app.route('/evaluate_answers', methods=['POST'])
def evaluate_answers_api():
    try:
        data = request.get_json()
        logging.info(f"📩 Received Evaluation Request: {data}")

        quiz = data.get("quiz", [])
        user_answers = data.get("answers", [])

        if not quiz or not user_answers:
            return jsonify({"error": "❌ Quiz or answers missing"}), 400

        # Ensure the length of answers matches the quiz questions
        if len(user_answers) != len(quiz):
            return jsonify({"error": "❌ The number of answers does not match the number of questions"}), 400

        evaluation = evaluate_answers(quiz, user_answers)
        return jsonify({"evaluation": evaluation})

    except Exception as e:
        logging.error(f"❌ Error in /evaluate_answers: {str(e)}")
        return jsonify({"error": f"❌ Server Error: {str(e)}"}), 500

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
