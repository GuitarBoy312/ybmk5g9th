import streamlit as st
from openai import OpenAI
import random
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 세션 상태에 현재 문제 유형을 저장하기 위한 키 추가
if 'reading_quiz_current_question_type' not in st.session_state:
    st.session_state.reading_quiz_current_question_type = None

# 앱에 새로 들어갈 때마다 초기화할 변수들
if 'reading_quiz_session_init' not in st.session_state:
    st.session_state.reading_quiz_session_init = False

if not st.session_state.reading_quiz_session_init:
    st.session_state.reading_quiz_total_questions = 0
    st.session_state.reading_quiz_correct_answers = 0
    st.session_state.reading_quiz_current_question = None
    st.session_state.reading_quiz_session_init = True

# 사이드바 컨테이너 생성
if 'reading_quiz_sidebar_placeholder' not in st.session_state:
    st.session_state.reading_quiz_sidebar_placeholder = st.sidebar.empty()

# 사이드바 업데이트 함수
def update_sidebar():
    st.session_state.reading_quiz_sidebar_placeholder.empty()
    with st.session_state.reading_quiz_sidebar_placeholder.container():
        st.write("## 읽기퀴즈 점수")
        st.write(f"총 문제 수: {st.session_state.reading_quiz_total_questions}")
        st.write(f"맞춘 문제 수: {st.session_state.reading_quiz_correct_answers}")
        if st.session_state.reading_quiz_total_questions > 0:
            accuracy = int((st.session_state.reading_quiz_correct_answers / st.session_state.reading_quiz_total_questions) * 100)
            st.write(f"정확도: {accuracy}%")

# 초기 사이드바 설정
update_sidebar()

def generate_essay_question():
    names = ["Marie", "Yena", "Juwon", "Emma", "Dave", "Linh", "Chanho"]
    name = random.choice(names)
    
    question_types = [
        ("장소", "에서 무엇을 했나요?"),
        ("활동", "을/를 하면서 무엇을 했나요?")
    ]
    question_type, question_ending = random.choice(question_types)

    activities = {
        "장소": [
            ("학교", "공부를 했다", "새로운 수학 개념을 배웠다"),
            ("공원", "산책을 했다", "아름다운 경치를 즐겼다"),
            ("도서관", "책을 읽었다", "흥미로운 과학책을 발견했다"),
            ("영화관", "영화를 봤다", "재미있는 코미디였다"),
            ("수영장", "수영을 했다", "자유형 기술을 향상시켰다"),
            ("동물원", "동물들을 구경했다", "코끼리가 가장 좋았다"),
            ("우주 센터", "우주선을 봤다", "우주 탐험에 대해 배웠다")
        ],
        "활동": [
            ("배드민턴을 치면서", "게임을 즐겼다", "친구들과 함께 재미있게 놀았다"),
            ("영화를 보면서", "팝콘을 먹었다", "카라멜 팝콘이 맛있었다"),
            ("자동차를 만들면서", "집중했다", "작은 장난감 자동차 모델을 완성했다"),
            ("낚시를 하면서", "기다렸다", "호수에서 물고기 세 마리를 잡았다"),
            ("쇼핑을 하면서", "옷을 골랐다", "새 옷을 샀다"),
            ("축구를 하면서", "골을 넣었다", "우리 팀이 경기에서 이겼다"),
            ("야구를 하면서", "공을 쳤다", "홈런을 쳤다")
        ]
    }

    activity_set = random.choice(activities[question_type])
    if question_type == "장소":
        location, action1, action2 = activity_set
        question = f"{name}은 {location}{question_ending}"
        dialogue = f"A: What did you do at the {location}, {name}?\nB: I {action1}. I {action2}."
    else:
        action, action1, action2 = activity_set
        question = f"{name}은 {action}{question_ending}"
        dialogue = f"A: What did you do while {action}, {name}?\nB: I {action1}. I {action2}."

    correct_answer = action2
    wrong_answers = [item[2] for item in activities[question_type] if item[2] != action2]
    options = random.sample(wrong_answers, 3) + [correct_answer]
    random.shuffle(options)

    return f"""
질문: {question}
대화: {dialogue}
선택지:
1. {options[0]}
2. {options[1]}
3. {options[2]}
4. {options[3]}
정답: {options.index(correct_answer) + 1}
"""

def generate_conversation_question():
    names = ["Marie", "Yena", "Juwon", "Emma", "Dave", "Linh", "Chanho"]
    activities = [
        "played badminton",
        "watched a movie",
        "made a car",
        "went fishing",
        "went shopping",
        "went to the museum",
        "played soccer",
        "played baseball",
        "learned about Korean history",
        "went to the space center"
    ]

    name = random.choice(names)
    activity = random.choice(activities)

    dialogue = f"""
A: {name}, what did you do yesterday?
B: I {activity}.
"""

    question = f"{name}은 어제 무엇을 했나요?"
    correct_answer = activity

    # 오답 생성
    wrong_answers = random.sample([a for a in activities if a != activity], 3)
    options = [activity] + wrong_answers
    random.shuffle(options)

    # 선택지를 한국어로 변환
    korean_activities = {
        "played badminton": "배드민턴을 쳤다",
        "watched a movie": "영화를 봤다",
        "made a car": "자동차를 만들었다",
        "went fishing": "낚시를 갔다",
        "went shopping": "쇼핑을 갔다",
        "went to the museum": "박물관에 갔다",
        "played soccer": "축구를 했다",
        "played baseball": "야구를 했다",
        "learned about Korean history": "한국 역사를 배웠다",
        "went to the space center": "우주 센터에 갔다"
    }

    korean_options = [korean_activities[opt] for opt in options]
    correct_answer = korean_activities[correct_answer]

    return f"""
[영어 대화]
{dialogue}

[한국어 질문]
질문: {question}
A. {korean_options[0]}
B. {korean_options[1]}
C. {korean_options[2]}
D. {korean_options[3]}
정답: {chr(65 + korean_options.index(correct_answer))}
"""

def generate_question():
    # 현재 문제 유형에 따라 다음 문제 유형 결정
    if st.session_state.reading_quiz_current_question_type == 'essay' or st.session_state.reading_quiz_current_question_type is None:
        question_type = 'conversation'
    else:
        question_type = 'essay'
    
    # 문제 유형 저장
    st.session_state.reading_quiz_current_question_type = question_type
    
    if question_type == 'essay':
        return generate_essay_question(), "essay"
    else:
        return generate_conversation_question(), "conversation"

def parse_question_data(data, question_type):
    lines = data.split('\n')
    if question_type == "essay":
        dialogue = ""
        question = ""
        options = []
        correct_answer = None

        for line in lines:
            if line.startswith("질문:"):
                question = line.replace("질문:", "").strip()
            elif line.startswith("대화:"):
                dialogue = line.replace("대화:", "").strip()
            elif re.match(r'^\d+\.', line):
                options.append(line.strip())
            elif line.startswith("정답:"):
                correct_answer = line.replace("정답:", "").strip()

        if correct_answer:
            correct_answer = int(re.search(r'\d+', correct_answer).group())

        # 디버깅을 위한 출력
        print(f"Parsed data: Question: {question}, Dialogue: {dialogue}, Options: {options}, Answer: {correct_answer}")

        return dialogue, question, options, correct_answer
    else:
        dialogue = ""
        question = ""
        options = []
        correct_answer = None

        dialogue_section = True
        for line in lines:
            if line.strip() == "[한국어 질문]":
                dialogue_section = False
                continue
            if dialogue_section:
                dialogue += line + "\n"
            else:
                if line.startswith("질문:"):
                    question = line.replace("질문:", "").strip()
                elif line.startswith(("A.", "B.", "C.", "D.")):
                    options.append(line.strip())
                elif line.startswith("정답:"):
                    correct_answer = line.replace("정답:", "").strip()

        # 정답에서 알파벳만 추출
        if correct_answer:
            correct_answer = correct_answer.split('.')[0].strip()

        return dialogue.strip(), question, options, correct_answer

def get_explanation_essay(question, passage, correct_answer, selected_option):
    prompt = f"""
    이 학생에게  정답이 무엇인지, 그들의 답변이 왜 틀렸는지, 학생이 방금 선택한 답변을 영어로 표현하면 무엇인지 설명해주세요. 
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.

    지문: {passage}

    문제: {question}
    정답: {correct_answer}
    학생의 선택: {selected_option}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 친절한 초등학교 영어 선생님입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def get_explanation_dialogue(question, dialogue, correct_answer, selected_option):
    prompt = f"""
    이 학생에게  정답이 무엇인지, 그들의 답변이 왜 틀렸는지, 학생이 방금 선택한 답변을 영어로 표현하면 무엇인지 설명해주세요.  
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.

    대화:
    {dialogue}

    문제: {question}
    정답: {correct_answer}
    학생의 선택: {selected_option}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 친절한 초등학교 영어 선생님입니다. 주어진 대화 내용만을 바탕으로 설명해야 합니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def main():
    # Streamlit UI
    st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♀️")
    st.subheader("어제 한 일에 대해 묻고 답하기 영어읽기 퀴즈🚵‍♂️")
    st.divider()

    #확장 설명
    with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
        st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 질문과 대화를 읽어보기<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

    if st.session_state.reading_quiz_current_question:
        if st.session_state.reading_quiz_current_question_type == "essay":
            passage, question, options, correct_answer = parse_question_data(st.session_state.reading_quiz_current_question, "essay")
            
            st.subheader("질문")
            st.write(question)

            st.divider()
            st.write(passage)
            st.divider()

            st.subheader("다음 중 알맞은 답을 골라보세요.")
            selected_option = st.radio("", options, index=None, key="essay_options")
            st.session_state.selected_option = selected_option

        else:
            dialogue, question, options, correct_answer = parse_question_data(st.session_state.reading_quiz_current_question, "conversation")
            
            st.markdown("### 질문")
            st.write(question)
            
            st.divider()
            st.text(dialogue)
            st.divider() 
            st.subheader("다음 중 알맞은 답을 골라보세요.")
            selected_option = st.radio("", options, index=None, key="conversation_options")
            st.session_state.selected_option = selected_option

        if st.button("정답 확인"):
            st.session_state.reading_quiz_total_questions += 1
            if st.session_state.selected_option:
                st.markdown(f"""
                <div style='background-color: #E6F3FF; padding: 10px; border-radius: 5px; margin-top: 10px;'>
                선택한 답: {st.session_state.selected_option}
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.reading_quiz_current_question_type == "essay":
                    selected_number = int(st.session_state.selected_option.split('.')[0].strip())
                    is_correct = selected_number == correct_answer
                else:
                    selected_letter = st.session_state.selected_option.split('.')[0].strip()
                    is_correct = selected_letter == correct_answer
                
                if is_correct:
                    st.success("정답입니다!")
                    st.session_state.reading_quiz_correct_answers += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}입니다.")
                    if st.session_state.reading_quiz_current_question_type == "essay":
                        explanation = get_explanation_essay(question, passage, correct_answer, st.session_state.selected_option)
                    else:
                        explanation = get_explanation_dialogue(question, dialogue, correct_answer, st.session_state.selected_option)
                    st.write(explanation)
                
                update_sidebar()
                st.session_state.reading_quiz_current_question = None
            else:
                st.warning("선택지를 선택하고 정답 확인 버튼을 눌러주세요.")
    else:
        st.info("아래의 '새 문제 만들기' 버튼을 눌러 퀴즈를 시작하세요.")

    if st.button("새 문제 만들기"):
        with st.spinner("새로운 문제를 생성 중입니다..."):
            st.session_state.reading_quiz_current_question, st.session_state.reading_quiz_current_question_type = generate_question()
        st.rerun()

if __name__ == "__main__":
    main()
