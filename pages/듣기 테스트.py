import streamlit as st
from openai import OpenAI
import random
import base64
import io

# OpenAI 클라이언트 초기화 (TTS용)
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 캐릭터 이름 목록과 성별
characters = {
    "Marie": "female", "Yena": "female", "Emma": "female", "Linh": "female",
    "Juwon": "male", "Dave": "male", "Chanho": "male"
}

# 활동 목록
activities = [
    ("배드민턴을 쳤다.", "played badminton. 🏸"),
    ("영화를 봤다.", "watched a movie. 🎬"),
    ("쇼핑을 갔다.", "went shopping. 🛍️"),
    ("박물관에 갔다.", "went to the museum. 🏛️"),
    ("축구를 했다.", "played soccer. ⚽"),
    ("낚시를 갔다.", "went fishing. 🎣"),
    ("역사를 공부했다.", "studied history. 📚"),
    ("우주 센터에 갔다.", "went to the space center. 🚀"),
    ("자동차를 만들었다.", "made a car. 🚗")
]

# 세션 상태 초기화
if 'listening_quiz_total_questions' not in st.session_state:
    st.session_state.listening_quiz_total_questions = 0
if 'listening_quiz_correct_answers' not in st.session_state:
    st.session_state.listening_quiz_correct_answers = 0
if 'listening_quiz_current_question' not in st.session_state:
    st.session_state.listening_quiz_current_question = None
if 'audio_tags' not in st.session_state:
    st.session_state.audio_tags = ""

# 활동 목록 순환을 위한 세션 상태 추가
if 'activity_index' not in st.session_state:
    st.session_state.activity_index = 0

# 사이드바 컨테이너 생성
if 'listening_quiz_sidebar_placeholder' not in st.session_state:
    st.session_state.listening_quiz_sidebar_placeholder = st.sidebar.empty()

# 사이드바 업데이트 함수
def update_sidebar():
    st.session_state.listening_quiz_sidebar_placeholder.empty()
    with st.session_state.listening_quiz_sidebar_placeholder.container():
        st.write("## 듣기퀴즈 점수")
        st.write(f"총 문제 수: {st.session_state.listening_quiz_total_questions}")
        st.write(f"맞춘 문제 수: {st.session_state.listening_quiz_correct_answers}")
        if st.session_state.listening_quiz_total_questions > 0:
            accuracy = int((st.session_state.listening_quiz_correct_answers / st.session_state.listening_quiz_total_questions) * 100)
            st.write(f"정확도: {accuracy}%")

# 초기 사이드바 설정
update_sidebar()

def generate_question():
    male_characters = [name for name, gender in characters.items() if gender == "male"]
    female_characters = [name for name, gender in characters.items() if gender == "female"]
    
    speaker_a = random.choice(male_characters)
    speaker_b = random.choice(female_characters)
    
    if random.choice([True, False]):
        speaker_a, speaker_b = speaker_b, speaker_a
    
    # 활동 목록에서 순차적으로 정답 선택
    correct_activity = activities[st.session_state.activity_index]
    st.session_state.activity_index = (st.session_state.activity_index + 1) % len(activities)
    
    wrong_activities = random.sample([a for a in activities if a != correct_activity], 3)
    
    all_options = [correct_activity] + wrong_activities
    random.shuffle(all_options)
    
    options = [f"{chr(65 + i)}. {option[0]}" for i, option in enumerate(all_options)]
    correct_answer = next(opt for opt in options if correct_activity[0] in opt)
    
    dialogue = f"{speaker_a}: What did you do yesterday, {speaker_b}?\n{speaker_b}: I {correct_activity[1]}"
    question = f"{speaker_b}는 어제 무엇을 했나요?"
    
    return {
        "question": question,
        "dialogue": dialogue,
        "options": options,
        "correct_answer": correct_answer,
        "speaker_a": speaker_a,
        "speaker_b": speaker_b
    }

def text_to_speech(text, gender):
    voice = "echo" if gender == "male" else "alloy"
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content
    except Exception as e:
        st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def generate_dialogue_audio(dialogue, speaker_a, speaker_b):
    lines = dialogue.split('\n')
    audio_contents = []
    
    for line in lines:
        speaker, text = line.split(': ', 1)
        gender = characters[speaker]
        audio_content = text_to_speech(text, gender)
        if audio_content:
            audio_contents.append(audio_content)
    
    return audio_contents

def create_audio_players(audio_contents):
    audio_tags = []
    for i, content in enumerate(audio_contents):
        audio_base64 = base64.b64encode(content).decode()
        audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        audio_tags.append(audio_tag)
    return "".join(audio_tags)

# Streamlit UI

st.header("✨인공지능 영어듣기 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("어제 한 일에 대해 묻고 답하기 영어듣기 퀴즈🚵‍♂️")
st.divider()

with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 재생 막대의 ▶ 버튼을 누르고 대화를 들어보기.<br>
    재생 막대의 오른쪽 스노우맨 버튼(점 세개)을 눌러 재생 속도를 조절할 수 있습니다.<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답과 대화 스크립트 확인하기.<br>
    ❗ 순서대로 하지 않거나 새 문제 만들기 버튼을 여러번 누르면 오류가 발생합니다.<br>
    🔁 그럴때에는 브라우저의 새로고침 버튼을 눌러주세요!<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 다시 눌러주세요.
    """
    ,  unsafe_allow_html=True)

if st.session_state.listening_quiz_current_question is not None:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    st.markdown("### 대화 듣기")
    st.write("왼쪽부터 순서대로 들어보세요. 너무 빠르면 눈사람 버튼을 눌러 속도를 조절해보세요.")
    st.markdown(st.session_state.audio_tags, unsafe_allow_html=True)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                correct_answer = st.session_state.correct_answer
                user_answer = selected_option
                
                #st.session_state.listening_quiz_total_questions += 1
                if user_answer == correct_answer:
                    st.success("정답입니다!")
                    st.session_state.listening_quiz_correct_answers += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}입니다.")
                
                st.text(st.session_state.dialogue)
                
                update_sidebar()
                st.session_state.listening_quiz_current_question = None
            else:
                st.warning("답을 선택해주세요.")

# "새 문제 만들기" 버튼
t=st.button("새 문제 만들기")
t.visible=False
if t:
    try:
        with st.spinner("새로운 문제를 생성 중입니다..."):
            qa_set = generate_question()
            
        st.session_state.question = qa_set["question"]
        st.session_state.dialogue = qa_set["dialogue"]
        st.session_state.options = qa_set["options"]
        st.session_state.correct_answer = qa_set["correct_answer"]
        st.session_state.listening_quiz_current_question = (qa_set["question"], qa_set["options"], qa_set["correct_answer"])
        
        audio_contents = generate_dialogue_audio(qa_set["dialogue"], qa_set["speaker_a"], qa_set["speaker_b"])
        st.session_state.audio_tags = create_audio_players(audio_contents)

        st.session_state.listening_quiz_total_questions += 1
        update_sidebar()
        st.rerun()
    except Exception as e:
        st.error(f"오류가 발생했습니다. 새문제 만들기 버튼을 다시 눌러주세요.: {str(e)}")
