# 🔮 사주 & RAG 시스템

Gemini API를 활용한 사주 분석과 RAG(Retrieval-Augmented Generation) 시스템을 통한 개인화된 조언을 제공하는 웹 애플리케이션입니다.

## ✨ 주요 기능

### 🔮 사주 분석
- **전체 사주 분석**: 생년월일시를 기반으로 상세한 사주 분석
- **오늘의 운세**: 실시간 일일 운세 제공
- **Gemini AI**: Google의 Gemini API를 활용한 정확한 사주 해석

### 📝 RAG 시스템
- **경험 저장**: 사용자의 과거 경험을 벡터로 변환하여 저장
- **유사 경험 검색**: 의미적 유사도를 기반으로 관련 경험 검색
- **개인화된 조언**: 과거 경험을 바탕으로 한 맞춤형 조언 제공

### 👤 사용자 관리
- 사용자 정보 등록 및 관리
- 사주 분석 결과 저장
- 경험 데이터 관리

## 🛠 기술 스택

- **프론트엔드**: React, TypeScript, CSS3
- **백엔드**: Python Flask
- **AI/ML**: Google Gemini API, Sentence Transformers
- **데이터베이스**: MySQL
- **개발 서버**: XAMPP

## 설치 및 실행 방법

### 1. XAMPP 설치 및 설정

1. [XAMPP 다운로드](https://www.apachefriends.org/download.html)에서 XAMPP를 다운로드하고 설치
2. XAMPP Control Panel을 실행
3. Apache와 MySQL 서비스를 시작

### 2. MySQL 데이터베이스 설정

1. XAMPP Control Panel에서 MySQL의 "Admin" 버튼 클릭 (phpMyAdmin 열림)
2. 새 데이터베이스 생성: `user_info_db`
3. 또는 `backend/database_setup.sql` 파일을 phpMyAdmin에서 실행

### 3. 환경 변수 설정

1. `backend` 폴더에 `.env` 파일 생성:
```env
# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key_here

# 데이터베이스 설정
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=user_info_db
```

2. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 Gemini API 키 발급

### 4. Python 백엔드 설정

```bash
# 백엔드 폴더로 이동
cd backend

# Python 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 필요한 패키지 설치
pip install -r requirements.txt

# Flask 서버 실행
python app.py
```

### 5. React 프론트엔드 실행

```bash
# 프로젝트 루트 폴더로 이동
cd ..

# React 앱 실행
npm start
```

## 📁 프로젝트 구조

```
user-info-site/
├── public/
├── src/
│   ├── components/
│   │   ├── UserInfoForm.tsx          # 사용자 정보 입력 폼
│   │   ├── UserInfoForm.css
│   │   ├── FortuneAnalysis.tsx       # 사주 분석 컴포넌트
│   │   ├── FortuneAnalysis.css
│   │   ├── ExperienceManager.tsx     # RAG 경험 관리 컴포넌트
│   │   └── ExperienceManager.css
│   ├── App.tsx
│   └── App.css
├── backend/
│   ├── app.py                        # Flask 메인 서버
│   ├── config.py                     # 설정 파일
│   ├── fortune_analyzer.py          # 사주 분석 모듈
│   ├── rag_system.py                # RAG 시스템 모듈
│   ├── requirements.txt
│   └── database_setup.sql
└── README.md
```

## 🔌 API 엔드포인트

### 사용자 관리
- `POST /api/users` - 사용자 정보 저장
- `GET /api/users` - 모든 사용자 정보 조회

### 사주 분석
- `POST /api/fortune/analyze` - 전체 사주 분석
- `POST /api/fortune/daily` - 오늘의 운세 조회

### RAG 시스템
- `POST /api/experience` - 사용자 경험 저장
- `POST /api/experience/search` - 유사한 경험 검색
- `POST /api/advice/personalized` - 개인화된 조언 생성

### 시스템
- `GET /api/health` - 서버 상태 확인

## 🚀 사용 방법

1. **사용자 등록**: 이름, 생년월일, 태어난 시간을 입력하여 계정 생성
2. **사주 분석**: 등록된 정보로 전체 사주 분석 또는 오늘의 운세 확인
3. **경험 저장**: 과거 경험이나 일상을 텍스트로 저장
4. **개인화된 조언**: 저장된 경험을 바탕으로 AI가 맞춤형 조언 제공

## ⚠️ 주의사항

- XAMPP의 MySQL이 실행 중이어야 합니다
- Gemini API 키가 필요합니다
- Python Flask 서버는 포트 5001에서 실행됩니다
- React 앱은 포트 3000에서 실행됩니다
- CORS가 설정되어 있어 React 앱에서 Flask API를 호출할 수 있습니다
- 첫 실행 시 Sentence Transformers 모델 다운로드로 인해 시간이 소요될 수 있습니다