import uvicorn
from fastapi import FastAPI
from chatbot import chat_router

app = FastAPI(title="LangChain Chatbot API", version="1.0")

# app/__init__.py에서 노출한 라우터를 앱에 등록
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": "LangChain 챗봇 서버가 정상 작동 중입니다."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
