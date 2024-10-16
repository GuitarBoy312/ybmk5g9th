import streamlit as st
from openai import OpenAI
import random
import base64
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 캐릭터와 성별 정의
characters = {
    "Marie": "female", "Yena": "female", "Emma": "female", "Linh": "female",
    "Juwon": "male", "Dave": "male", "Chanho": "male"
}

# 세션 상태 초기화
if 'listening_quiz_total_questions' not in st.session_state:
    st.session_state.listening_quiz_total_questions = 0
if 'listening_quiz_correct_answers' not in st.session_state:
    st.session_state.listening_quiz_correct_answers = 0
if 'listening_quiz_current_question' not in st.session_state:
    st.session_state.listening_quiz_current_question = None
if 'audio_tags' not in st.session_state:
    st.session_state.audio_tags = ""

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

# 미리 정의된 선택지 (모두 한국어로)
predefined_options = [
    "배드민턴을 쳤다.",
    "영화를 봤다.",
    "쇼핑을 갔다.",
    "박물관에 갔다.",
    "축구를 했다.",
    "낚시를 갔다.",
    "역사를 공부했다.",
    "우주 센터에 갔다.",
    "자동차를 만들었다."
]

def generate_question():
    try:
        questions = [
            "What did you do yesterday, {name}?"
        ]
        
        answers = [
            "I played badminton. 🏸",
            "I watched a movie. 🎬",
            "I went shopping. 🛍️",
            "I went to the museum. 🏛️",
            "I played soccer. ⚽",
            "I went fishing. 🎣",
            "I learned about Korean history. 📚",
            "I went to the space center. 🚀",
            "I made a car. 🚗"
        ]
        
        korean_questions = [
            "{name}은(는) 어제 무엇을 했나요?"
        ]
        
        selected_question = random.choice(questions)
        selected_answer = random.choice(answers)
        selected_korean_question = random.choice(korean_questions)
        
        male_speakers = [name for name, gender in characters.items() if gender == "male"]
        female_speakers = [name for name, gender in characters.items() if gender == "female"]
        speaker_a = random.choice(male_speakers)
        speaker_b = random.choice(female_speakers)
        
        if random.choice([True, False]):
            speaker_a, speaker_b = speaker_b, speaker_a

        formatted_question = selected_question.format(name=speaker_b)
        
        dialogue = f"""
{speaker_a}: {formatted_question}
{speaker_b}: {selected_answer}
"""

        correct_answer_korean = next((opt for opt in predefined_options if opt.split()[0] in selected_answer.lower()), random.choice(predefined_options))

        wrong_options = random.sample([opt for opt in predefined_options if opt != correct_answer_korean], 3)
        
        all_options = [correct_answer_korean] + wrong_options
        random.shuffle(all_options)

        options = [f"{chr(65 + i)}. {option}" for i, option in enumerate(all_options)]

        correct_answer = next(opt for opt in options if correct_answer_korean in opt)

        return dialogue, selected_korean_question.format(name=speaker_b), options, correct_answer
    except Exception as e:
        st.error(f"문제 생성 중 오류가 발생했습니다: {str(e)}")
        return None, None, None, None

def split_dialogue(text):
    lines = text.strip().split('\n')
    speakers = {}
    for line in lines:
        match = re.match(r'([A-Z][a-z]+):\s*(.*)', line)
        if match:
            speaker, content = match.groups()
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(content)
    return speakers

def text_to_speech(text, speaker):
    try:
        voice = "nova" if characters[speaker] == "female" else "echo"
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        audio_bytes = response.content
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        
        return audio_tag
    except Exception as e:
        st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")
        return ""

def generate_dialogue_audio(dialogue):
    try:
        speakers = split_dialogue(dialogue)
        audio_tags = []
        
        for speaker, lines in speakers.items():
            text = " ".join(lines)
            audio_tag = text_to_speech(text, speaker)
            audio_tags.append(audio_tag)
        
        return "".join(audio_tags)
    except Exception as e:
        st.error(f"대화 오디오 생성 중 오류가 발생했습니다: {str(e)}")
        return ""

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
                
                st.session_state.listening_quiz_total_questions += 1
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
if st.button("새 문제 만들기"):
    try:
        with st.spinner("새로운 문제를 생성 중입니다..."):
            dialogue, question, options, correct_answer = generate_question()
        
        if dialogue and question and options and correct_answer:
            st.session_state.question = question
            st.session_state.dialogue = dialogue.strip()
            st.session_state.options = options
            st.session_state.correct_answer = correct_answer
            st.session_state.listening_quiz_current_question = (question, options, correct_answer)
            
            st.session_state.audio_tags = generate_dialogue_audio(st.session_state.dialogue)
            
            update_sidebar()
            st.rerun()
        else:
            st.error("문제 생성에 실패했습니다. 다시 시도해주세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다. 새문제 만들기 버튼을 다시 눌러주세요.: {str(e)}")
