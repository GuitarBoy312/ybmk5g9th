import streamlit as st
import random

sentences = [
    ("I played badminton yesterday.", "🏸"),
    ("I watched a movie last night.", "🎬"),
    ("I made a car model last weekend.", "🚗"),
    ("I went fishing last Sunday.", "🎣"),
    ("I went shopping yesterday afternoon.", "🛍️"),
    ("I visited the museum last week.", "🏛️"),
    ("I played soccer with friends yesterday.", "⚽"),
    ("I played baseball last Saturday.", "⚾"),
    ("I learned about Korean history last month.", "📚"),
    ("I visited the space center last summer.", "🚀"),
    ("What did you do yesterday?", "🤔")
]

# 세션 상태 초기화
if 'question_order' not in st.session_state:
    st.session_state.question_order = list(range(len(sentences)))
    random.shuffle(st.session_state.question_order)
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None

def generate_question():
    if st.session_state.current_question_index >= len(sentences):
        random.shuffle(st.session_state.question_order)
        st.session_state.current_question_index = 0
    
    sentence_index = st.session_state.question_order[st.session_state.current_question_index]
    sentence, emoji = sentences[sentence_index]
    words = sentence.split()
    past_tense_verbs = [word for word in words if word.endswith('ed') or word in ['went', 'made', 'did']]
    
    correct_word = random.choice(past_tense_verbs)
    blank_index = words.index(correct_word)
    
    blanked_sentence = ' '.join(words[:blank_index] + ['_____'] + words[blank_index+1:])
    
    st.session_state.current_question_index += 1
    
    return blanked_sentence, emoji, correct_word

st.title("과거 동사 퀴즈")

# 문제 수와 정답 수 표시
st.write(f"총 문제 수: {st.session_state.total_questions}")
st.write(f"맞춘 문제 수: {st.session_state.correct_answers}")

if st.session_state.current_question is None:
    st.session_state.current_question = generate_question()
    st.session_state.total_questions += 1

blanked_sentence, emoji, correct_word = st.session_state.current_question
st.write(emoji)
st.write(blanked_sentence)

user_answer = st.text_input("빈칸에 들어갈 단어를 입력하세요:")

if st.button("정답 확인"):
    if user_answer.lower() == correct_word.lower():
        st.success("정답입니다!")
        st.session_state.correct_answers += 1
    else:
        st.error(f"틀렸습니다. 정답은 {correct_word}입니다.")
    
    st.session_state.current_question = None
    st.rerun()

# 새 문제 만들기 버튼
if st.button("새 문제 만들기"):
    st.session_state.current_question = None
    st.rerun()
