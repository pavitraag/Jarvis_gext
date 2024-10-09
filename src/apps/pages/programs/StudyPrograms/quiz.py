import streamlit as st
import requests
import random

def get_quiz_data(category=None, difficulty=None, question_count=5):
    """
    Fetches quiz questions from the Open Trivia Database API.
    
    Parameters:
        category (int): Category ID for the trivia.
        difficulty (str): Difficulty level ('easy', 'medium', 'hard').
        question_count (int): Number of questions to retrieve.
    
    Returns:
        list: A list of questions with options and answers.
    """
    base_url = "https://opentdb.com/api.php?"
    
    # Build the API URL with the chosen parameters
    url = f"{base_url}amount={question_count}"
    
    if category:
        url += f"&category={category}"
    
    if difficulty:
        url += f"&difficulty={difficulty}"
    
    url += "&type=multiple"  # Multiple choice questions
    
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error("Failed to retrieve questions. Please try again later.")
        return []
    
    data = response.json()
    
    if data["response_code"] != 0:
        st.error("No questions found for the selected options.")
        return []
    
    return data["results"]

def display_question(question_data, question_idx):
    """
    Displays a single quiz question using Streamlit and handles answer submission and navigation.
    
    Parameters:
        question_data (dict): Contains question, options, and correct answer.
        question_idx (int): Index of the question.
    
    Returns:
        None
    """
    # Extract question details
    question = question_data['question']
    correct_answer = question_data['correct_answer']
    incorrect_answers = question_data['incorrect_answers']
    
    # Combine correct and incorrect answers
    if f"all_answers_{question_idx}" not in st.session_state:
        st.session_state[f"all_answers_{question_idx}"] = incorrect_answers + [correct_answer]
        random.shuffle(st.session_state[f"all_answers_{question_idx}"])  # Shuffle once and store it

    all_answers = st.session_state[f"all_answers_{question_idx}"]

    # Display the question
    st.write(f"**Question {question_idx + 1}:** {question}")
    
    # Store the selected answer in session state
    if f"selected_{question_idx}" not in st.session_state:
        st.session_state[f"selected_{question_idx}"] = None
    
    # Let the user select an answer and store it in session state
    selected_answer = st.radio(
        "Select your answer:", all_answers, key=f"q{question_idx}", index=all_answers.index(st.session_state[f"selected_{question_idx}"]) if st.session_state[f"selected_{question_idx}"] else 0
    )
    
    # Handle answer submission and feedback
    if st.button("Submit Answer", key=f"submit_{question_idx}"):
        st.session_state[f"selected_{question_idx}"] = selected_answer  # Save the selected answer

        if selected_answer == correct_answer:
            st.success("Correct!")
            st.session_state.score += 1
        else:
            st.error(f"Wrong! The correct answer was: {correct_answer}")
        
        # Move to the next question
        st.session_state.current_question += 1

def start_quiz():
    st.title("Quiz Generator")
    st.write("Customize your quiz and test your knowledge!")
    
    # Quiz customization
    category_input = st.text_input("Enter category ID (leave blank for random):", "")
    
    # Check if the input is numeric before converting
    if category_input.isdigit():
        category = int(category_input)
    elif category_input.strip() == "":
        category = None
    else:
        st.error("Invalid category ID. Please enter a valid number or leave it blank for random.")
        return  # Stop further execution if invalid input
    
    difficulty = st.selectbox("Select difficulty level:", ["Random", "Easy", "Medium", "Hard"], index=0)
    difficulty = difficulty.lower() if difficulty != "Random" else None
    
    question_count = st.slider("Number of questions:", 1, 20, 5)
    
    # Start quiz button
    if st.button("Start Quiz"):
        # Fetch quiz data
        quiz_data = get_quiz_data(category, difficulty, question_count)
        
        if quiz_data:
            # Initialize session state variables for tracking score and current question
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.quiz_finished = False
            st.session_state.quiz_data = quiz_data

    # Display current question if the quiz has started and is not finished
    if 'quiz_data' in st.session_state and not st.session_state.quiz_finished:
        current_question_idx = st.session_state.current_question
        
        # Check if quiz has finished
        if current_question_idx < len(st.session_state.quiz_data):
            current_question_data = st.session_state.quiz_data[current_question_idx]
            display_question(current_question_data, current_question_idx)
        else:
            st.write(f"### Quiz finished! Your final score is {st.session_state.score}/{len(st.session_state.quiz_data)}.")
            st.session_state.quiz_finished = True

# Main function for Streamlit
if __name__ == "__main__":
    start_quiz()
