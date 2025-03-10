import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from audiorecorder import audiorecorder
import io

# OpenAI API 키 설정
if 'openai_client' not in st.session_state:
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])

# 시스템 메시지 정의
SYSTEM_MESSAGE = {
    "role": "system", 
    "content": '''
    너는 초등학교 영어교사야. 나는 초등학생이고, 나와 영어로 대화하는 연습을 해 줘. 영어공부와 관계없는 질문에는 대답할 수 없어. 그리고 나는 무조건 영어로 말할거야. 내 발음이 좋지 않더라도 영어로 인식하도록 노력해 봐.            
    [대화의 제목]
    What did you do yesterday?
    [지시]
    1. 내가 너에게 [질문] 중 하나를 골라 질문을 할거야. 
    2. 너는 내 질문을 듣고, [대답] 중 하나를 무작위로 골래 대답을 해.
    3. 그 후, 너는 바로 이어서 [질문] 중 하나를 무작위로 골라 질문해. 
       그러면 내가 대답을 할거야.
    4. 내가 또 질문을 하면 [대답]을 무작위로 선택해서 대답해.
    5. 내가 그만하자고 할 때까지 계속 주고 받으며 대화하자.
    [질문]
    What did you do yesterday?
    
    [대답]
    I played badminton. 🏸
    I watched a movie. 🎬
    I made a car. 🚗
    I went fishing. 🎣
    I went shopping. 🛍️
    I went to the museum. 🏛️
    I played soccer. ⚽
    I played baseball. ⚾
    I learned about Korean history. 📚
    I went to the space center. 🚀
    '''
}

# 초기화 함수 수정
def initialize_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['openai_client'] = OpenAI(api_key=st.secrets["openai_api_key"])
    st.session_state['chat_history'] = [SYSTEM_MESSAGE]
    st.session_state['initialized'] = True
    st.session_state['page'] = '대화 훈련'  # 현재 페이지 표시

# 세션 상태 초기화 로직 수정
if 'initialized' not in st.session_state or not st.session_state['initialized'] or st.session_state.get('page') != '대화 훈련':
    initialize_session()

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    st.session_state['chat_history'].append({"role": "user", "content": prompt})
    response = st.session_state['openai_client'].chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['chat_history']
    )
    assistant_response = response.choices[0].message.content
    st.session_state['chat_history'].append({"role": "assistant", "content": assistant_response})
    return assistant_response

# 음성을 녹음하고 텍스트로 변환하는 함수
def record_and_transcribe():
    audio = audiorecorder("녹음 시작", "녹음 완료", pause_prompt="잠깐 멈춤")
    
    if len(audio) > 0:
        st.success("녹음이 완료되었습니다. 변환 중입니다...")
        st.write("내가 한 말 듣기")
        st.audio(audio.export().read())
        
        audio_bytes = io.BytesIO()
        audio.export(audio_bytes, format="wav")
        audio_file = io.BytesIO(audio_bytes.getvalue())
        audio_file.name = "audio.wav"
        transcription = st.session_state['openai_client'].audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text
    
    return None

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech_openai(text):
    try:
        response = st.session_state['openai_client'].audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )
        st.write("인공지능 선생님의 대답 듣기")    
        st.audio(response.content)
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

# Streamlit UI
st.header("✨인공지능 영어대화 선생님 잉글링👩‍🏫")
st.subheader("누구의 물건인지 묻고 답하기🧦")
st.divider()

# 처음부터 다시하기 버튼
if st.button("처음부터 다시하기", type="primary"):
    initialize_session()
    st.rerun()

# 확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [녹음 시작] 버튼을 눌러 잉글링에게 말하기.<br>
    2️⃣ [녹음 완료] 버튼을 누르고 내가 한 말과 잉글링의 대답 들어보기.<br> 
    3️⃣ 재생 막대의 버튼으로 재생▶ 및 정지⏸,<br>
       재생 막대의 오른쪽 스노우맨 버튼(점 세개)을 눌러 재생 속도를 조절할 수 있습니다.<br> 
    4️⃣ [녹음 시작] 버튼을 다시 눌러 대답하고 이어서 바로 질문하기.<br>
    5️⃣ 1~3번을 반복하기. 말문이 막힐 땐 [잠깐 멈춤] 버튼을 누르기.<br>
    <br>
    🙏 잉글링은 완벽하게 이해하거나 제대로 대답하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [처음부터 다시하기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)
    st.divider()
    st.write("다음 보기와 같이 잉글링에게 질문과 대답을 해 보세요.")
    st.markdown('''                 
    [질문]<br>
    🔸Whose sock is this?<br>
    🔸Whose textbook is this?<br>
    🔸Whose scarf is this? <br>
    🔸Whose button is this? <br>
    🔸Whose towel is this?<br>
    <br>
    [대답]<br>
    🔹It’s mine.<br>
    🔹It’s Harry’s.<br>
    🔹It’s Lisa’s. <br>
    🔹It’s Kevin’s. <br>
    ❓ 어렵다면 잉글링의 답변을 따라하는 것도 좋은 방법이예요.
''', unsafe_allow_html=True)

    
# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    user_input_text = record_and_transcribe()
    if user_input_text:
        response = get_chatgpt_response(user_input_text)
        if response:
            text_to_speech_openai(response)

# 사이드바 구성
with st.sidebar:
    st.header("대화 기록")
    for message in st.session_state['chat_history'][1:]:  # 시스템 메시지 제외
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
