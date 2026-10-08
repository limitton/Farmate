import os
import sys
import json
from PyQt5.QtCore import Qt, QUrl, pyqtSlot  # pyqtSlot 임포트 위치 정리
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel

# langchain 및 LLM 관련 소스코드
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# ------------------------------------------------------------------
# [1] 클로바 챗봇 백엔드 연동
# ------------------------------------------------------------------
def load_persona(persona_name: str, folder_path: str = "./personas") -> str:
    file_path = os.path.join(folder_path, f"{persona_name}.txt")
    if not os.path.exists(file_path):
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"당신은 {persona_name} 페르소나를 가진 인공지능입니다. 친절하게 답변하세요.")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

persona_system_prompt = load_persona("lion")

model = ChatOpenAI(
    model="HCX-007",
    base_url="https://clovastudio.stream.ntruss.com/v1/openai",
    api_key="nv-f5f203197385450c802d459aed95f5f8koHd",
)

prompt = ChatPromptTemplate.from_messages([
    ("system", persona_system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

chain = prompt | model
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

brain_chain = RunnableWithMessageHistory(
    chain, get_session_history, input_messages_key="question", history_messages_key="history"
)
config = {"configurable": {"session_id": "user_1234"}}

# ------------------------------------------------------------------
# [2] 웹 브라우저(HTML/JS)와 PyQt5 파이썬 간 양방향 통신 브릿지
# ------------------------------------------------------------------
class ChatBridge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(str, result=str)
    def ask_ai(self, user_question):
        # 웹 프론트엔드에서 질문을 받아 파이썬 LangChain 실행
        response = brain_chain.invoke({"question": user_question}, config=config)
        return response.content

# 챗봇 UI를 장식할 심플하고 예쁜 HTML 테마
CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; background: #f4f5f7; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 93vh; }
        #chat-window { flex: 1; overflow-y: auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 15px; max-width: 70%; word-break: break-all; line-height: 1.5; }
        .user { background: #fee500; align-self: flex-end; margin-left: auto; color: #000; }
        .assistant { background: #e9e9eb; align-self: flex-start; color: #000; }
        #input-container { display: flex; gap: 10px; }
        input { flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; }
        button { padding: 0 25px; background: #333; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold;}
        button:hover { background: #555; }
    </style>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        var bridge;
        new QWebChannel(qt.webChannelTransport, function (channel) {
            bridge = channel.objects.bridge;
        });

        function sendMessage() {
            var input = document.getElementById('user-input');
            var text = input.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            input.value = '';

            // 파이썬 백엔드로 질문 던지기
            bridge.ask_ai(text, function(response) {
                appendMessage(response, 'assistant');
            });
        }

        function appendMessage(text, sender) {
            var win = document.getElementById('chat-window');
            var msgDiv = document.createElement('div');
            msgDiv.className = 'message ' + sender;
            msgDiv.innerText = text;
            win.appendChild(msgDiv);
            win.scrollTop = win.scrollHeight;
        }

        function handleKeyPress(e) {
            if (e.keyCode === 13) { sendMessage(); }
        }
    </script>
</head>
<body>
    <h2 style="margin-top:0; color:#333;">🦁 클로바 에이전트 챗봇</h2>
    <div id="chat-window">
        <div class="message assistant">발표가 완료되었습니다! 질문을 입력해주세요.</div>
    </div>
    <div id="input-container">
        <!-- 💡 오타 수정: handleKeyPress(e) -> handleKeyPress(event) -->
        <input type="text" id="user-input" placeholder="메시지를 입력하세요..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">전송</button>
    </div>
</body>
</html>
"""

# ------------------------------------------------------------------
# [3] 메인 PPT 윈도우 (PyQt5)
# ------------------------------------------------------------------
class PPTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # PPT로 띄울 이미지 리스트 (파일이 실제 경로에 있어야 합니다)
        self.images = ["1.png", "2.png", "3.png", "4.png"]
        self.current_index = 0

        self.initUI()

    def initUI(self):
        # 창 관리 스택 위젯 생성
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 1. 이미지용 라벨 스택 추가
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;") # 여백은 검은색 처리
        self.stacked_widget.addWidget(self.image_label)

        # 2. 챗봇용 웹뷰 스택 추가
        self.web_view = QWebEngineView()
        self.bridge = ChatBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        self.web_view.setHtml(CHAT_HTML)
        self.stacked_widget.addWidget(self.web_view)

        # 첫 번째 이미지 로드 및 전체 화면 전환
        self.update_image()
        self.showFullScreen()

    def update_image(self):
        """현재 인덱스의 이미지를 화면 크기에 맞춰 꽉 채워 출력"""
        if self.current_index < len(self.images):
            img_path = self.images[self.current_index]
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                # 모니터 화면 크기에 맞춰 이미지 스케일 조정 (비율 유지)
                screen_geometry = QApplication.primaryScreen().geometry()
                scaled_pixmap = pixmap.scaled(screen_geometry.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText(f"이미지를 찾을 수 없습니다:\n{img_path}\n\n(화면을 클릭하면 넘어갑니다)")
                self.image_label.setStyleSheet("color: white; font-size: 24px; background-color: black;")

    def mousePressEvent(self, event):
        """화면 어디든 마우스를 클릭했을 때 발생하는 이벤트"""
        # 현재 슬라이드 쇼 진행 중일 때만 클릭 작동
        if self.stacked_widget.currentIndex() == 0:
            self.current_index += 1

            # 아직 보여줄 사진이 남았다면 다음 사진 표시
            if self.current_index < len(self.images):
                self.update_image()
            # 사진이 끝나면 챗봇 화면 스택으로 전환
            else:
                self.stacked_widget.setCurrentIndex(1)
                self.showNormal()
                self.resize(1024, 768)

    def keyPressEvent(self, event):
        """ESC 키를 누르면 프로그램 종료 기능 추가"""
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PPTWindow()
    # 💡 에러 수정: 존재하지 않는 exec_with_context() 메서드를 exec_()로 변경
    sys.exit(app.exec_())
