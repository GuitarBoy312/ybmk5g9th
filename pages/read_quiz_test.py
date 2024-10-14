import streamlit as st
from openai import OpenAI
import random
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 세션 상태 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.total_questions = 0
    st.session_state.correct_answers = 0
    st.session_state.current_question_type = None
    st.session_state.question_data = None
    st.session_state.selected_option = None
    st.session_state.show_answer = False
    st.session_state.last_checked_option = None
    st.session_state.explanation = None

def generate_essay_question():
    name = random.choice(["Marie", "Yena", "Juwon", "Emma", "Dave", "Linh", "Chanho"])
    question = "What did you do yesterday?"
    answer = random.choice([
        "I played badminton.",
        "I watched a movie.",
        "I made a car.",
        "I went fishing.",
        "I went shopping",
        "I went to the museum.",
        "I played soccer",
        "I played baseball",
        "I learned about Korean history.",
        "I went to the space center."
    ])
    question_format = f"{name}은 어제 무엇을 했나요?"

    key_expression = f'''
    A: {question}, {name}
    B: {answer}
    '''
    prompt = f"""
    {answer}을 이용해 1문장 짜리 짧은 영어 에세이를 만들어 주세요.
    그 다음, 대화 내용에 관한 간단한 질문을 한국어로 만들어주세요. 
    마지막으로, 질문에 대한 4개의 선택지를 초등학생이 이해하기 쉬운 한국어로 제공해주세요. 
    정답은 선택지 중 하나여야 합니다.
    출력 형식:
    질문: {question_format}
    대화: (영어 대화)
    선택지:
    1. (선택지 1)
    2. (선택지 2)
    3. (선택지 3)
    4. (선택지 4)
    정답: (정답 번호)
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content" : "너는 EFL 환경의 초등학교 영어교사야. 초등학생에 맞는 쉬운 한국어와 영어를 사용해."},
            {"role": "user", "content": prompt}]
    )
    
    # 응답 내용 로깅
    print("GPT Response:", response.choices[0].message.content)
    
    return response.choices[0].message.content

def generate_conversation_question():
    name = random.choice(["Marie", "Yena", "Juwon", "Emma", "Dave", "Linh", "Chanho"])
    question = "What did you do yesterday?"
    answer = random.choice([
        "I played badminton.",
        "I watched a movie.",
        "I made a car.",
        "I went fishing.",
        "I went shopping",
        "I went to the museum.",
        "I played soccer",
        "I played baseball",
        "I learned about Korean history.",
        "I went to the space center."
    ])
    question_format = random.choice(["무엇에 대해 묻고있나요?","{name}은 어제 무엇을 했나요?"])    

    key_expression = f'''
    A: {name}, {question}
    B: {answer}
    '''
    prompt = f"""{key_expression}으로 영어 대화를 생성해주세요. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요. 
    조건: 문제의 정답은 1개 입니다. 
    A와 B가 대화할 때 A가 B의 이름을 부르면서 대화를 합니다. B의 이름은 {name} 입니다.
    영어 대화는 A와 B가 각각 1번 말하고 끝납니다.
    형식:
    [영어 대화]
    A: ...
    B: ...

    [한국어 질문]
    조건: {question_format}을 만들어야 합니다. 영어 대화에서 생성된 A와 B의 이름 중 필요한 것을 골라서 질문에 사용해야 합니다.
    질문: (한국어로 된 질문) 이 때, 선택지는 한국어로 제공됩니다.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def generate_question():
    # 현재 문제 유형에 따라 다음 문제 유형 결정
    if st.session_state.current_question_type == 'essay' or st.session_state.current_question_type is None:
        question_type = 'conversation'
    else:
        question_type = 'essay'
    
    # 문제 유형 저장
    st.session_state.current_question_type = question_type
    
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
    st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♀️")
    st.subheader("어제 한 일에 대해 묻고 답하기 영어읽기 퀴즈🚵‍♂️")
    st.divider()

    # 통계 표시
    st.sidebar.markdown(f"### 퀴즈 통계")
    st.sidebar.markdown(f"총 문제 수: {st.session_state.total_questions}")
    st.sidebar.markdown(f"맞춘 문제 수: {st.session_state.correct_answers}")

    if st.button("새로운 문제 생성"):
        st.session_state.question_data, st.session_state.question_type = generate_question()
        st.session_state.selected_option = None
        st.session_state.show_answer = False
        st.session_state.last_checked_option = None
        st.session_state.explanation = None
        st.session_state.total_questions += 1
        st.rerun()

    if st.session_state.question_data:
        if st.session_state.question_type == "essay":
            passage, question, options, correct_answer = parse_question_data(st.session_state.question_data, "essay")
        else:
            dialogue, question, options, correct_answer = parse_question_data(st.session_state.question_data, "conversation")
        
        st.markdown("### 질문")
        st.write(question)
        
        st.divider()
        if st.session_state.question_type == "essay":
            st.write(passage)
        else:
            st.text(dialogue)
        st.divider()

        st.subheader("다음 중 알맞은 답을 골라보세요.")
        selected_option = st.radio("", options, index=None, key="quiz_options")
        st.session_state.selected_option = selected_option

        if st.button("정답 확인"):
            st.session_state.show_answer = True
            st.session_state.last_checked_option = st.session_state.selected_option

            if st.session_state.selected_option:
                if st.session_state.question_type == "essay":
                    selected_number = int(st.session_state.selected_option.split('.')[0].strip())
                    is_correct = selected_number == correct_answer
                else:
                    selected_letter = st.session_state.selected_option.split('.')[0].strip()
                    is_correct = selected_letter == correct_answer
                
                if is_correct:
                    st.session_state.correct_answers += 1
                    st.success("정답입니다!")
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}입니다.")
                    if st.session_state.question_type == "essay":
                        st.session_state.explanation = get_explanation_essay(question, passage, correct_answer, st.session_state.selected_option)
                    else:
                        st.session_state.explanation = get_explanation_dialogue(question, dialogue, correct_answer, st.session_state.selected_option)
                    st.write(st.session_state.explanation)
                
                st.rerun()
            else:
                st.warning("선택지를 선택하고 정답 확인 버튼을 눌러주세요.")

if __name__ == "__main__":
    main()
