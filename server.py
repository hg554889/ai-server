import json
import difflib
import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY2")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")

# JSON 데이터 로딩 함수
def load_json_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"JSON 파일을 읽는 중 오류 발생: {file_path}")
        return []

# 학습 및 테스트 데이터 로딩
train_data = load_json_data("F:\\ai_server\\mbpp_train.json")
test_data = load_json_data("F:\\ai_server\\mbpp_test.json")
qa_data = train_data + test_data
questions = [item["instruction"] for item in qa_data]

# 텍스트 번역 함수
def translate_text(text, target_lang="en"):
    prompt = f"Translate the following text into {target_lang}:\n{text}"
    try:
        response = gemini_model.generate_content([prompt])
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            return text
    except Exception as e:
        print(f"🔴 번역 오류: {e}")
        return text

# 질문과 가장 유사한 항목 찾기 함수
def find_best_match(user_question):
    english_question = translate_text(user_question, target_lang="en")
    closest_matches = difflib.get_close_matches(english_question, questions, n=1, cutoff=0.5)
    if closest_matches:
        match = closest_matches[0]
        for item in qa_data:
            if item["instruction"] == match:
                return item["response"]
    return "관련된 코드 예제를 찾을 수 없습니다."

# /chat 엔드포인트: POST 요청으로 질문을 받고 답변 반환
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get("question", "")
    if not user_question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400

    # 사용자 질문 영어 번역
    english_question = translate_text(user_question, target_lang="en")
    # 최적 매칭 응답 찾기 (영어로 된 응답)
    response = find_best_match(english_question)
    # 응답을 한국어로 번역
    korean_response = translate_text(response, target_lang="ko")

    return jsonify({
        "original_question": user_question,
        "translated_question": english_question,
        "response": korean_response
    })

# 기본 라우트 예시 (서버 동작 확인용)
@app.route('/', methods=['GET'])
def home():
    return "AI 챗봇 서버가 정상 동작 중입니다."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
