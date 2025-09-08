import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'user_info_db'),
    'charset': 'utf8mb4'
}

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
