from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# API 키 설정
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Flask 앱 생성
app = Flask(__name__)


def ask_gemini(question: str):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "질문이 없습니다."}), 400

    answer = ask_gemini(question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
