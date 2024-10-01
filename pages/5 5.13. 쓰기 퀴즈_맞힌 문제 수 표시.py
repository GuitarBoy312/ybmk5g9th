import streamlit as st
import random

# 문장과 이모지 목록
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
    ("What did you do yesterday?", "🤔")  # 이 문장을 다시 추가했습니다.
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

def generate_question():
    if st.session_state.current_question_index >= len(sentences):
        # 모든 문제를 다 풀었으면 순서를 다시 섞고 처음부터 시작
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

# Streamlit UI
st.title("과거 동사 퀴즈")

# 문제 수와 정답 수 표시
st.write(f"총 문제 수: {st.session_state.total_questions}")
st.write(f"맞춘 문제 수: {st.session_state.correct_answers}")

# 확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 빈칸에 들어갈 단어를 고르세요.<br> 
    3️⃣ [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    , unsafe_allow_html=True)

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False
    st.session_state.blanked_sentence = ""
    st.session_state.emoji = ""
    st.session_state.correct_word = ""

if st.session_state.question_generated:
    st.markdown("### 문제")
    st.write("빈칸에 들어갈 단어를 입력하세요:")
    st.markdown(f'<p style="font-size: 24px; margin-top: 10px;">{st.session_state.blanked_sentence} {st.session_state.emoji}</p>', unsafe_allow_html=True)
      
    with st.form(key='answer_form'):
        user_input = st.text_input("정답을 입력하세요:", key="user_answer")
        submit_button = st.form_submit_button(label='정답 확인')

        if submit_button:
            if user_input:
                st.info(f"입력한 답: {user_input}")
                
                # 사용자 입력과 정답을 소문자로 변환하고 마침표와 물음표를 제거
                user_answer = user_input.lower().rstrip('.?').replace("'", "")
                correct_answer = st.session_state.correct_word.lower().rstrip('.?').replace("'", "")
                
                # 축약형을 풀어쓴 형태로 변환
                expanded_correct_answer = correct_answer.replace("im", "i am")
                expanded_user_answer = user_answer.replace("im", "i am")
                
                # 정답 비교 시 마지막 물음표 유무와 관계없이 비교
                if user_answer.rstrip('?') == correct_answer.rstrip('?') or \
                   expanded_user_answer.rstrip('?') == expanded_correct_answer.rstrip('?'):  
                    st.success("정답입니다!")
                    st.markdown(f'<p style="font-size: 24px;">정답 문장: {st.session_state.blanked_sentence.replace("_____", st.session_state.correct_word)} {st.session_state.emoji}</p>', unsafe_allow_html=True)
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_word}입니다.")
                    st.markdown(f'<p style="font-size: 24px;">정답 문장: {st.session_state.blanked_sentence.replace("_____", st.session_state.correct_word)} {st.session_state.emoji}</p>', unsafe_allow_html=True)
            else:
                st.warning("답을 입력해주세요.")

# 새 문제 만들기 버튼을 페이지 맨 아래로 이동
if st.button("새 문제 만들기"):
    blanked_sentence, emoji, correct_word = generate_question()
    
    st.session_state.blanked_sentence = blanked_sentence
    st.session_state.emoji = emoji
    st.session_state.correct_word = correct_word
    st.session_state.question_generated = True
    st.session_state.total_questions += 1
    
    # 페이지 새로고침
    st.rerun()
