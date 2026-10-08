import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. 특정 폴더에서 페르소나 txt 파일 가져오기
def load_persona(persona_name: str, folder_path: str = "./personas") -> str:
    """
    특정 폴더에 있는 txt 파일에서 페르소나 텍스트를 읽어옵니다.
    예: load_persona("doctor") -> ./persona/doctor.txt 파일 로드
    """
    file_path = os.path.join(folder_path, f"{persona_name}.txt")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"페르소나 파일을 찾을 수 없습니다: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

# 2. 페르소나 로드 (예: 'detective.txt' 파일을 가져옴)
# txt 내부 예시: "당신은 냉철하고 예리한 탐정입니다. 모든 답변을 탐정의 말투로 작성하세요."
persona_system_prompt = load_persona("lion")


# 3. LLM 설정 및 프롬프트 템플릿 생성
model = ChatOpenAI(
    model="HCX-005",  # 예: "llama3", "mistral" 등
    base_url="https://clovastudio.stream.ntruss.com/v1/openai",  # Ollama, vLLM 등의 OpenAI 호환 Base URL
    api_key="nv-f5f203197385450c802d459aed95f5f8koHd",  # 로컬 LLM의 경우 임의의 값 입력 가능
)

prompt = ChatPromptTemplate.from_messages([
    ("system", persona_system_prompt),       # txt 파일에서 불러온 페르소나 주입
    MessagesPlaceholder(variable_name="history"), # 대화 기억이 들어갈 자리
    ("human", "{question}")                  # 사용자의 질문
])

# 4. 체인 구성 (LCEL)
chain = prompt | model

# 5. 메모리(기억) 저장소 설정
# 실무에서는 InMemory 대신 RedisChatMessageHistory 나 SQLChatMessageHistory 등을 사용해 영구 저장 가능
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 6. 기억이 결합된 최종 런어블(Runnable) 생성
brain_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history"
)

# 7. 대화 실행 테스트 (세션 ID 지정)
config = {"configurable": {"session_id": "user_1234"}}

# 첫 번째 질문
response1 = brain_chain.invoke({"question": "10만원짜리 노트북을 살까 아니면 100만원짜리 노트북을 살까?"}, config=config)
print(f"{response1.content}\n")
