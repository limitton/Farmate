from openai import OpenAI

client = OpenAI(
    api_key="nv-3f1151bb8f5d4e4a8df381283a84776bfKSG",  # CLOVA Studio API 키
    base_url="https://clovastudio.stream.ntruss.com/v1/openai"  # CLOVA Studio 오픈AI 호환 API URL
)

# Chat Completions
response = client.chat.completions.create(
    model="HCX-007",  # CLOVA Studio 지원 모델명
    messages=[
        {"role": "system", "content": "당신은 유능한 AI 어시스턴트입니다."},
        {"role": "user", "content": "인공지능에 대해 설명해 주세요."}
    ]
)

print(response.choices[0].message.content)
