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
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None

# 사이드바 컨테이너 생성
if 'sidebar_placeholder' not in st.session_state:
    st.session_state.sidebar_placeholder = st.sidebar.empty()

# 사이드바 업데이트 함수
def update_sidebar():
    st.session_state.sidebar_placeholder.empty()
    with st.session_state.sidebar_placeholder.container():
        st.write("## 퀴즈 진행 상황")
        st.write(f"총 문제 수: {st.session_state.total_questions}")
        st.write(f"맞춘 문제 수: {st.session_state.correct_answers}")
        if st.session_state.total_questions > 0:
            accuracy = (st.session_state.correct_answers / st.session_state.total_questions) * 100
            st.write(f"정확도: {accuracy:.2f}%")

# 초기 사이드바 설정
update_sidebar()

def generate_question():
    questions = [
        "What did you do yesterday, {name}?"
    ]
    
    answers = [
        "I played badminton. 🏸",
        "I watched a movie. 🎬",
        "I made a car. 🚗",
        "I went fishing. 🎣",
        "I went shopping. 🛍️",
        "I went to the museum. 🏛️",
        "I played soccer. ⚽",
        "I played baseball. ⚾",
        "I learned about Korean history. 📚",
        "I went to the space center. 🚀"
    ]
    
    korean_questions = [
        "{name}은(는) 어제 무엇을 했나요?"
    ]
    
    selected_question = random.choice(questions)
    selected_answer = random.choice(answers)
    selected_korean_question = random.choice(korean_questions)
    
    # 성별이 다른 두 화자 선택
    male_speakers = [name for name, gender in characters.items() if gender == "male"]
    female_speakers = [name for name, gender in characters.items() if gender == "female"]
    speaker_a = random.choice(male_speakers)
    speaker_b = random.choice(female_speakers)
    
    # 무작위로 순서 결정
    if random.choice([True, False]):
        speaker_a, speaker_b = speaker_b, speaker_a

    formatted_question = selected_question.format(name=speaker_b)
    
    key_expression = f"""
{speaker_a}: {formatted_question}
{speaker_b}: {selected_answer}
"""
    prompt = f"""{key_expression}을 생성해주세요. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.  
    조건: 문제의 정답은 1개입니다.  
    영어 대화는 A와 B가 각각 1번씩 말하고 끝납니다.
    A는 다음과 같이 한문장을 말하세요.
    B는 다음과 같이 한문장을 말하세요.
    형식:
    [영어 대화]
    A: {speaker_a}: {formatted_question}
    B: {speaker_b}: {selected_answer}


    [한국어 질문]
    조건: {selected_korean_question.format(name=speaker_b)}을 만들어야 합니다.
    (한국어로 된 질문) 이 때, 선택지는 한국어로 제공됩니다.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류 발생: {str(e)}")
        return None

def split_dialogue(text):
    lines = text.strip().split('\n')
    speakers = {}
    for line in lines:
        match = re.match(r'([A-Z]):\s*(.*)', line)
        if match:
            speaker, content = match.groups()
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(content)
    return speakers

def text_to_speech(text, speaker):
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

def generate_dialogue_audio(dialogue):
    speakers = split_dialogue(dialogue)
    audio_tags = []
    
    for speaker, lines in speakers.items():
        text = " ".join(lines)
        speaker_name = re.search(r'([A-Za-z]+):', lines[0]).group(1)  # 대화에서 화자 이름 추출
        audio_tag = text_to_speech(text, speaker_name)
        audio_tags.append(audio_tag)
    
    return "".join(audio_tags)

def generate_explanation(question, correct_answer, user_answer, dialogue):
    prompt = f"""
    다음 영어 대화와 관련된 질문에 대해 학생이 오답을 선택했습니다. 
    대화: {dialogue}
    질문: {question}
    정답: {correct_answer}
    학생의 답변: {user_answer}
    
    이 학생에게 왜 그들의 답변이 틀렸는지, 그리고 정답이 무엇인지 설명해주세요. 
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어듣기 퀴즈 선생님 퀴즐링🕵️‍♀️")
st.subheader("어제 한 일에 대해 묻고 답하기 영어듣기 퀴즈🚵‍♂️")
st.divider()

#확장 설명
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
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

if st.session_state.current_question is not None:
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
                # 정답 비교 로직 수정
                correct_answer = st.session_state.correct_answer
                user_answer = selected_option
                
                # 디버깅을 위한 출력
                st.write(f"정답: {correct_answer}")
                st.write(f"사용자 답변: {user_answer}")
                
                if user_answer == correct_answer:
                    st.success("정답입니다!")
                    st.session_state.correct_answers += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}입니다.")
                
                st.text(st.session_state.dialogue)
                
                update_sidebar()
                st.session_state.current_question = None
            else:
                st.warning("답을 선택해주세요.")

# "새 문제 만들기" 버튼을 페이지 맨 아래로 이동
if st.button("새 문제 만들기"):
    try:
        with st.spinner("새로운 문제를 생성 중입니다..."):
            full_content = generate_question()
        
        if full_content is None:
            st.error("문제 생성에 실패했습니다. 다시 시도해 주세요.")
            st.stop()
        
        if "[한국어 질문]" not in full_content:
            st.error("문제 형식이 올바르지 않습니다. 다시 시도해 주세요.")
            st.stop()
        
        dialogue, question_part = full_content.split("[한국어 질문]")
        
        question_lines = question_part.strip().split("\n")
        question = question_lines[0].replace("질문:", "").strip() if question_lines else ""
        options = [line.strip() for line in question_lines[1:5] if line.strip()]
        correct_answer = ""
        
        for line in question_lines:
            if line.startswith("정답:"):
                correct_answer = line.replace("정답:", "").strip()
                break
        
        if not question or not options or not correct_answer:
            st.error("문제 형식이 올바르지 않습니다. 다시 시도해 주세요.")
            st.stop()
        
        if correct_answer not in options:
            st.error("생성된 정답이 옵션에 없습니다. 다시 시도해 주세요.")
            st.stop()
        
        st.session_state.question = question
        st.session_state.dialogue = dialogue.strip()
        st.session_state.options = options
        st.session_state.correct_answer = correct_answer
        st.session_state.current_question = (question, options, correct_answer)
        
        st.session_state.audio_tags = generate_dialogue_audio(st.session_state.dialogue)
        
        st.session_state.total_questions += 1
        update_sidebar()
        st.rerun()
    except Exception as e:
        st.error(f"문제 생성 중 오류가 발생했습니다: {str(e)}")
