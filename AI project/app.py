import streamlit as st
import json
import random
import os

# ------------------- CONFIG -------------------
QUIZ_FILE = "questions.json"
HISTORY_FILE = "history.json"
TOTAL_HINTS = 2
QUESTIONS_PER_QUIZ = 10

# ------------------- LOAD QUIZ -------------------
def load_quiz():
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        questions = []
        for diff in data['questions']:
            questions.extend(data['questions'][diff])
        random.shuffle(questions)
        return questions[:QUESTIONS_PER_QUIZ]  # only 10 questions
    except Exception as e:
        st.error(f"Failed to load quiz: {e}")
        return []

# ------------------- SAVE HISTORY -------------------
def save_history(name, score, total):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append({"name": name, "score": score, "total": total})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

# ------------------- SESSION STATE -------------------
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "hints_used" not in st.session_state:
    st.session_state.hints_used = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ------------------- QUIZ LOGIC -------------------
def next_question():
    st.session_state.quiz_index += 1
    st.session_state.selected_option = None
    st.session_state.submitted = False

def check_answer():
    q = st.session_state.questions[st.session_state.quiz_index]
    correct_index = q['answer_index']
    if st.session_state.selected_option == correct_index:
        st.session_state.score += 1
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Wrong! Correct answer: {q['options'][correct_index]}")
    st.session_state.submitted = True

# ------------------- STREAMLIT UI -------------------
st.title("🎓 AI Quiz Bot")

name = st.text_input("Enter your name:")

if st.button("Start Quiz") and name.strip():
    st.session_state.questions = load_quiz()
    st.session_state.quiz_index = 0
    st.session_state.score = 0
    st.session_state.hints_used = 0
    st.session_state.selected_option = None
    st.session_state.submitted = False

# Show questions
if st.session_state.questions and st.session_state.quiz_index < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.quiz_index]
    st.subheader(f"Question {st.session_state.quiz_index+1}: {q['question']}")

    # Hint button
    if q.get("hint") and st.session_state.hints_used < TOTAL_HINTS:
        if st.button(f"💡 Hint ({TOTAL_HINTS - st.session_state.hints_used} left)"):
            st.info(f"💡 Hint: {q['hint']}")
            st.session_state.hints_used += 1

    # Radio options
    st.session_state.selected_option = st.radio("Select your answer:", 
                                                options=list(range(len(q['options']))),
                                                format_func=lambda x: q['options'][x],
                                                key=f"q{st.session_state.quiz_index}")

    # Submit button
    if not st.session_state.submitted:
        if st.button("Submit Answer"):
            check_answer()

    # Next question button (only after submit)
    if st.session_state.submitted:
        if st.button("Next Question"):
            next_question()

# Quiz completed
else:
    if st.session_state.questions:
        st.header("🏆 Quiz Completed")
        st.write(f"**{name}**, Your Score: {st.session_state.score}/{len(st.session_state.questions)}")
        save_history(name, st.session_state.score, len(st.session_state.questions))
