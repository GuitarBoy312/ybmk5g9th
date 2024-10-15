import streamlit as st
import random

sentences = [
    ("I played badminton yesterday.", "나는 어제 배드민턴을 쳤어요.", "🏸"),
    ("I watched a movie last night.", "나는 어젯밤에 영화를 봤어요.", "🎬"),
    ("I made a car model last weekend.", "나는 지난 주말에 자동차 모형을 만들었어요.", "🚗"),
    ("I went fishing last Sunday.", "나는 지난 일요일에 낚시를 갔어요.", "🎣"),
    ("I went shopping yesterday afternoon.", "나는 어제 오후에 쇼핑을 갔어요.", "🛍️"),
    ("I visited the museum last week.", "나는 지난주에 박물관을 방문했어요.", "🏛️"),
    ("I played soccer with friends yesterday.", "나는 어제 친구들과 축구를 했어요.", "⚽"),
    ("I played baseball last Saturday.", "나는 지난 토요일에 야구를 했어요.", "⚾"),
    ("I learned about Korean history last month.", "나는 지난달에 한국 역사에 대해 배웠어요.", "📚"),
    ("I visited the space center last summer.", "나는 지난 여름에 우주 센터를 방문했어요.", "🚀"),
    ("What did you do yesterday?", "너는 어제 무엇을 했니?", "🤔")
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
    sentence, translation, emoji = sentences[sentence_index]
    words = sentence.split()
    past_tense_verbs = [word for word in words if word.endswith('ed') or word in ['went', 'made', 'did']]
    
    correct_word = random.choice(past_tense_verbs)
    blank_index = words.index(correct_word)
    
    blanked_words = words.copy()
    blanked_words[blank_index] = '_____'
    blanked_sentence = ' '.join(blanked_words)
    
    st.session_state.current_question_index += 1
    
    return blanked_sentence, translation, emoji, correct_word

# 전역 변수로 사이드바 컨테이너 생성
sidebar_container = st.sidebar.container()

# 사이드바 업데이트 함수
def update_sidebar():
    global sidebar_container
    sidebar_container.empty()
    with sidebar_container:
        st.write("## 퀴즈 진행 상황")
        st.write(f"총 문제 수: {st.session_state.total_questions}")
        st.write(f"맞춘 문제 수: {st.session_state.correct_answers}")

# 초기 사이드바 설정
update_sidebar()

st.header("✨인공지능 영어문장 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("어제 한 일에 대해 묻고 답하기 영어쓰기 퀴즈🚵‍♂️")
st.divider()

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

if st.session_state.current_question is not None:
    blanked_sentence, translation, emoji, correct_word = st.session_state.current_question
    st.markdown(f"### {blanked_sentence} {emoji}")
    st.write(f"해석: {translation}")

    user_answer = st.text_input("빈칸에 들어갈 단어를 입력하세요:")

    if st.button("정답 확인"):
        st.write(f"입력한 답: {user_answer}")
        
        if user_answer.lower() == correct_word.lower():
            st.success("정답입니다!")
            st.session_state.correct_answers += 1
            update_sidebar()
        else:
            st.error(f"틀렸습니다. 정답은 {correct_word}입니다.")
        
        full_sentence = blanked_sentence.replace('_____', correct_word)
        st.markdown(f"### 정답 문장: {full_sentence} {emoji}")
        
        st.session_state.current_question = None

# "새 문제 만들기" 버튼
if st.button("새 문제 만들기"):
    st.session_state.current_question = generate_question()
    st.session_state.total_questions += 1
    update_sidebar()
    st.rerun()
