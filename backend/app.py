from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import re
from datetime import datetime
from config import DB_CONFIG, GEMINI_API_KEY
from fortune_analyzer import FortuneAnalyzer
from rag_system import RAGSystem

app = Flask(__name__)
CORS(app)  # CORS 설정으로 React 앱에서 API 호출 가능

# 사주 분석기와 RAG 시스템 초기화
fortune_analyzer = None
rag_system = None
RAG_AVAILABLE = False

if GEMINI_API_KEY:
    try:
        fortune_analyzer = FortuneAnalyzer()
        rag_system = RAGSystem()
        RAG_AVAILABLE = True
        print("사주 분석기와 RAG 시스템이 성공적으로 초기화되었습니다.")
    except Exception as e:
        print(f"시스템 초기화 오류: {e}")
else:
    print("GEMINI_API_KEY가 설정되지 않았습니다. 사주 분석 기능이 비활성화됩니다.")

def get_db_connection():
    """데이터베이스 연결을 반환합니다."""
    try:
        # 한자 처리를 위한 연결 설정
        connection = pymysql.connect(
            **DB_CONFIG,
            use_unicode=True,
            autocommit=False
        )
        return connection
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def validate_hanja_name(name):
    """한자 이름 검증 함수"""
    if not name or not isinstance(name, str):
        return False
    
    # 한자 범위: 기본 한자(U+4E00~U+9FFF) + 확장 한자(U+3400~U+4DBF) + 호환 한자(U+F900~U+FAFF)
    hanja_pattern = re.compile(r'^[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+$')
    
    # 길이 검증 (2-4글자)
    if len(name) < 2 or len(name) > 4:
        return False
    
    return bool(hanja_pattern.match(name))

def init_database():
    """데이터베이스와 테이블을 초기화합니다."""
    try:
        # 데이터베이스 생성 (한자 처리 최적화)
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4',
            use_unicode=True
        )
        
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # 사용자 정보 테이블 생성 (한자 처리 최적화)
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL COMMENT '이름 (한자)',
                birth_date DATE NOT NULL COMMENT '생년월일',
                birth_time TIME NOT NULL COMMENT '태어난 시간',
                message TEXT NOT NULL COMMENT '할말',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보 테이블'
            """
            cursor.execute(create_users_table)
            
            # 사용자 프로필 테이블 생성 (RAG용 개인화 데이터)
            create_user_profiles_table = """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL COMMENT '사용자 ID',
                financial_status VARCHAR(50) COMMENT '재정상태',
                occupation VARCHAR(100) COMMENT '직업',
                interests TEXT COMMENT '관심분야',
                current_challenges TEXT COMMENT '현재 고민',
                goals TEXT COMMENT '목표',
                personality_traits TEXT COMMENT '성격특성',
                relationship_status VARCHAR(50) COMMENT '연애상태',
                health_concerns TEXT COMMENT '건강관심사',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 프로필 테이블'
            """
            cursor.execute(create_user_profiles_table)
            
            # 사주 분석 결과 테이블 생성
            create_fortune_table = """
            CREATE TABLE IF NOT EXISTS fortune_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL COMMENT '사용자 ID',
                analysis_result TEXT NOT NULL COMMENT '사주 분석 결과',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사주 분석 결과 테이블'
            """
            cursor.execute(create_fortune_table)
            
            # 사용자 경험 데이터 테이블 생성 (RAG용)
            create_experiences_table = """
            CREATE TABLE IF NOT EXISTS user_experiences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL COMMENT '사용자 ID',
                experience_text TEXT NOT NULL COMMENT '경험 내용',
                experience_date DATE COMMENT '경험 날짜',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 경험 데이터 테이블'
            """
            cursor.execute(create_experiences_table)
            
            # 한자 처리를 위한 인덱스 추가
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_birth_date ON users(birth_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_birth_time ON users(birth_time)")
                print("한자 처리용 인덱스가 생성되었습니다.")
            except Exception as idx_error:
                print(f"인덱스 생성 중 오류 (무시 가능): {idx_error}")
            
            connection.commit()
            print("데이터베이스와 테이블이 성공적으로 생성되었습니다.")
            
    except Exception as e:
        print(f"데이터베이스 초기화 오류: {e}")
    finally:
        if connection:
            connection.close()

@app.route('/api/users', methods=['POST'])
def create_user():
    """새로운 사용자 정보를 저장합니다."""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'birthDate', 'birthTime', 'message']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 한자 이름 검증
        if not validate_hanja_name(data['name']):
            return jsonify({'error': '이름은 2-4글자의 한자만 입력해주세요.'}), 400
        
        # 데이터베이스 연결
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
        
        with connection.cursor() as cursor:
            # 사용자 정보 삽입
            insert_query = """
            INSERT INTO users (name, birth_date, birth_time, message)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data['name'],
                data['birthDate'],
                data['birthTime'],
                data['message']
            ))
            connection.commit()
            
            # 삽입된 사용자 ID 반환
            user_id = cursor.lastrowid
            
        connection.close()
        
        return jsonify({
            'message': '사용자 정보가 성공적으로 저장되었습니다.',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        print(f"사용자 생성 오류: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """모든 사용자 정보를 조회합니다."""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, birth_date, birth_time, message, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
            
        connection.close()
        
        return jsonify({'users': users}), 200
        
    except Exception as e:
        print(f"사용자 조회 오류: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """특정 사용자 정보를 조회합니다."""
    try:
        print(f"사용자 조회 요청: user_id = {user_id}")
        connection = get_db_connection()
        if not connection:
            print("데이터베이스 연결 실패")
            return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, birth_date, birth_time, message, created_at
                FROM users
                WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            print(f"조회된 사용자: {user}")
            
        connection.close()
        
        if user:
            # datetime 객체를 문자열로 변환
            if user.get('birth_date'):
                user['birth_date'] = user['birth_date'].strftime('%Y-%m-%d')
            if user.get('birth_time'):
                user['birth_time'] = str(user['birth_time'])
            if user.get('created_at'):
                user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"변환된 사용자: {user}")
            return jsonify(user), 200
        else:
            print("사용자를 찾을 수 없음")
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
    except Exception as e:
        print(f"사용자 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@app.route('/api/fortune/analyze', methods=['POST'])
def analyze_fortune():
    """사주를 분석합니다."""
    if not fortune_analyzer:
        return jsonify({'error': '사주 분석 기능이 비활성화되어 있습니다.'}), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'birthDate', 'birthTime']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 한자 이름 검증
        if not validate_hanja_name(data['name']):
            return jsonify({'error': '이름은 2-4글자의 한자만 입력해주세요.'}), 400
        
        # 사용자 프로필 조회
        profile_data = None
        rag_context = ""
        if 'userId' in data:
            connection = get_db_connection()
            if connection:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM user_profiles 
                        WHERE user_id = %s
                    """, (data['userId'],))
                    profile_data = cursor.fetchone()
                connection.close()
            
            # RAG 컨텍스트 생성
            if rag_system:
                rag_context = rag_system.get_user_context_for_fortune(data['userId'])
        
        # 사주 분석 수행 (프로필 데이터 + RAG 컨텍스트 포함)
        analysis_result = fortune_analyzer.analyze_fortune(
            data['name'],
            data['birthDate'],
            data['birthTime'],
            data.get('message', ''),
            profile_data,
            data.get('userId'),
            rag_context
        )
        
        # 데이터베이스에 분석 결과 저장
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                # 사용자 ID 찾기 (이름과 생년월일로)
                cursor.execute("""
                    SELECT id FROM users 
                    WHERE name = %s AND birth_date = %s AND birth_time = %s
                    ORDER BY created_at DESC LIMIT 1
                """, (data['name'], data['birthDate'], data['birthTime']))
                
                user_result = cursor.fetchone()
                if user_result:
                    user_id = user_result[0]
                    
                    # 최근 5분 내에 같은 사용자의 분석 결과가 있는지 확인
                    cursor.execute("""
                        SELECT id FROM fortune_analysis 
                        WHERE user_id = %s AND created_at > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                        ORDER BY created_at DESC LIMIT 1
                    """, (user_id,))
                    
                    recent_analysis = cursor.fetchone()
                    
                    if not recent_analysis:
                        # 분석 결과 저장
                        cursor.execute("""
                            INSERT INTO fortune_analysis (user_id, analysis_result)
                            VALUES (%s, %s)
                        """, (user_id, analysis_result))
                        connection.commit()
                        
                        # RAG 컨텍스트로도 저장
                        if rag_system:
                            rag_system.save_fortune_analysis_context(user_id, analysis_result)
                    else:
                        print(f"사용자 {user_id}의 최근 분석 결과가 있어 중복 저장을 방지했습니다.")
            
            connection.close()
        
        return jsonify({
            'message': '사주 분석이 완료되었습니다.',
            'analysis': analysis_result
        }), 200
        
    except Exception as e:
        print(f"사주 분석 오류: {e}")
        return jsonify({'error': '사주 분석 중 오류가 발생했습니다.'}), 500


@app.route('/api/experience', methods=['POST'])
def save_experience():
    """사용자 경험을 저장합니다."""
    if not RAG_AVAILABLE or not rag_system:
        return jsonify({'error': 'RAG 시스템이 비활성화되어 있습니다.'}), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['userId', 'experienceText']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 경험 저장
        success = rag_system.save_experience(
            data['userId'],
            data['experienceText'],
            data.get('experienceDate')
        )
        
        if success:
            return jsonify({'message': '경험이 성공적으로 저장되었습니다.'}), 201
        else:
            return jsonify({'error': '경험 저장에 실패했습니다.'}), 500
        
    except Exception as e:
        print(f"경험 저장 오류: {e}")
        return jsonify({'error': '경험 저장 중 오류가 발생했습니다.'}), 500

@app.route('/api/experience/search', methods=['POST'])
def search_experiences():
    """유사한 경험을 검색합니다."""
    if not RAG_AVAILABLE or not rag_system:
        return jsonify({'error': 'RAG 시스템이 비활성화되어 있습니다.'}), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['userId', 'query']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 유사한 경험 검색
        similar_experiences = rag_system.search_similar_experiences(
            data['userId'],
            data['query'],
            data.get('topK', 5)
        )
        
        return jsonify({
            'message': '경험 검색이 완료되었습니다.',
            'experiences': similar_experiences
        }), 200
        
    except Exception as e:
        print(f"경험 검색 오류: {e}")
        return jsonify({'error': '경험 검색 중 오류가 발생했습니다.'}), 500

@app.route('/api/advice/personalized', methods=['POST'])
def get_personalized_advice():
    """개인화된 조언을 제공합니다."""
    if not RAG_AVAILABLE or not rag_system:
        return jsonify({'error': 'RAG 시스템이 비활성화되어 있습니다.'}), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['userId', 'query']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 개인화된 조언 생성
        advice = rag_system.get_personalized_advice(
            data['userId'],
            data['query']
        )
        
        return jsonify({
            'message': '개인화된 조언이 생성되었습니다.',
            'advice': advice
        }), 200
        
    except Exception as e:
        print(f"개인화된 조언 생성 오류: {e}")
        return jsonify({'error': '개인화된 조언 생성 중 오류가 발생했습니다.'}), 500

@app.route('/api/profile', methods=['POST'])
def save_user_profile():
    """사용자 프로필을 저장합니다."""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['userId']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
        
        with connection.cursor() as cursor:
            # 기존 프로필이 있는지 확인
            cursor.execute("SELECT id FROM user_profiles WHERE user_id = %s", (data['userId'],))
            existing_profile = cursor.fetchone()
            
            if existing_profile:
                # 기존 프로필 업데이트
                update_query = """
                UPDATE user_profiles SET
                    financial_status = %s,
                    occupation = %s,
                    interests = %s,
                    current_challenges = %s,
                    goals = %s,
                    personality_traits = %s,
                    relationship_status = %s,
                    health_concerns = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """
                cursor.execute(update_query, (
                    data.get('financialStatus'),
                    data.get('occupation'),
                    data.get('interests'),
                    data.get('currentChallenges'),
                    data.get('goals'),
                    data.get('personalityTraits'),
                    data.get('relationshipStatus'),
                    data.get('healthConcerns'),
                    data['userId']
                ))
            else:
                # 새 프로필 생성
                insert_query = """
                INSERT INTO user_profiles 
                (user_id, financial_status, occupation, interests, current_challenges, 
                 goals, personality_traits, relationship_status, health_concerns)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    data['userId'],
                    data.get('financialStatus'),
                    data.get('occupation'),
                    data.get('interests'),
                    data.get('currentChallenges'),
                    data.get('goals'),
                    data.get('personalityTraits'),
                    data.get('relationshipStatus'),
                    data.get('healthConcerns')
                ))
            
            connection.commit()
        
        connection.close()
        
        return jsonify({'message': '프로필이 성공적으로 저장되었습니다.'}), 201
        
    except Exception as e:
        print(f"프로필 저장 오류: {e}")
        return jsonify({'error': '프로필 저장 중 오류가 발생했습니다.'}), 500

@app.route('/api/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """사용자 프로필을 조회합니다."""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
        
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM user_profiles 
                WHERE user_id = %s
            """, (user_id,))
            profile = cursor.fetchone()
        
        connection.close()
        
        if profile:
            return jsonify({'profile': profile}), 200
        else:
            return jsonify({'message': '프로필을 찾을 수 없습니다.'}), 404
        
    except Exception as e:
        print(f"프로필 조회 오류: {e}")
        return jsonify({'error': '프로필 조회 중 오류가 발생했습니다.'}), 500

@app.route('/api/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    """유사한 사용자들을 조회합니다."""
    if not RAG_AVAILABLE or not rag_system:
        return jsonify({'error': 'RAG 시스템이 비활성화되어 있습니다.'}), 503
    
    try:
        # 유사한 사용자들 검색
        similar_users = rag_system.find_similar_users(user_id, max_similar=5)
        
        return jsonify({
            'message': '유사한 사용자 검색이 완료되었습니다.',
            'similar_users': similar_users
        }), 200
        
    except Exception as e:
        print(f"유사한 사용자 검색 오류: {e}")
        return jsonify({'error': '유사한 사용자 검색 중 오류가 발생했습니다.'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태를 확인합니다."""
    return jsonify({'status': 'OK', 'message': '서버가 정상적으로 작동 중입니다.'}), 200

if __name__ == '__main__':
    # 데이터베이스 초기화
    init_database()
    
    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5001)
