import pymysql
from config import DB_CONFIG
import re
from datetime import datetime

class RAGSystem:
    def __init__(self):
        # MySQL 기반 RAG 시스템으로 단순화
        pass
    
    def get_db_connection(self):
        """데이터베이스 연결을 반환합니다."""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            return connection
        except Exception as e:
            print(f"데이터베이스 연결 오류: {e}")
            return None
    
    def save_experience(self, user_id, experience_text, experience_date=None):
        """사용자 경험을 저장합니다."""
        try:
            connection = self.get_db_connection()
            if not connection:
                return False
            
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO user_experiences (user_id, experience_text, experience_date)
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (
                    user_id,
                    experience_text,
                    experience_date
                ))
                connection.commit()
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"경험 저장 오류: {e}")
            return False
    
    def search_similar_experiences(self, user_id, query_text, top_k=5):
        """사용자 정보를 고려한 MySQL 기반 키워드 검색으로 유사한 경험을 찾습니다."""
        try:
            connection = self.get_db_connection()
            if not connection:
                return []
            
            # 사용자 기본 정보 조회
            user_info = self.get_user_basic_info(user_id)
            
            # 쿼리에서 키워드 추출 (사용자 정보 고려)
            keywords = self.extract_keywords_with_user_context(query_text, user_info)
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 사용자 정보를 고려한 검색 쿼리
                if keywords:
                    keyword_conditions = " OR ".join([f"experience_text LIKE %s" for _ in keywords])
                    keyword_params = [f"%{keyword}%" for keyword in keywords]
                    
                    # 사용자 정보와 관련된 추가 검색 조건 (생년월일/시간 우선)
                    user_context_conditions = []
                    if user_info:
                        # 생년월일 관련 키워드 검색 (최우선)
                        birth_keywords = self.extract_birth_date_keywords(user_info)
                        for birth_keyword in birth_keywords:
                            if birth_keyword in query_text.lower():
                                user_context_conditions.append("experience_text LIKE %s")
                                keyword_params.append(f"%{birth_keyword}%")
                        
                        # 태어난 시간 관련 키워드 검색 (2순위)
                        time_keywords = self.extract_birth_time_keywords(user_info)
                        for time_keyword in time_keywords:
                            if time_keyword in query_text.lower():
                                user_context_conditions.append("experience_text LIKE %s")
                                keyword_params.append(f"%{time_keyword}%")
                        
                        # 사용자 이름 (3순위)
                        if user_info.get('name'):
                            user_context_conditions.append("experience_text LIKE %s")
                            keyword_params.append(f"%{user_info['name']}%")
                    
                    # 모든 조건을 OR로 결합
                    all_conditions = keyword_conditions
                    if user_context_conditions:
                        all_conditions += " OR " + " OR ".join(user_context_conditions)
                    
                    # 관련도 점수 계산을 위한 CASE 문 구성 (생년월일/시간 최우선)
                    case_conditions = []
                    case_params = []
                    
                    # 1순위: 생년월일 관련 키워드 (1.0점)
                    if user_info:
                        birth_keywords = self.extract_birth_date_keywords(user_info)
                        for birth_keyword in birth_keywords:
                            if birth_keyword in query_text.lower():
                                case_conditions.append("WHEN experience_text LIKE %s THEN 1.0")
                                case_params.append(f"%{birth_keyword}%")
                    
                    # 2순위: 태어난 시간 관련 키워드 (0.9점)
                    if user_info:
                        time_keywords = self.extract_birth_time_keywords(user_info)
                        for time_keyword in time_keywords:
                            if time_keyword in query_text.lower():
                                case_conditions.append("WHEN experience_text LIKE %s THEN 0.9")
                                case_params.append(f"%{time_keyword}%")
                    
                    # 3순위: 사용자 이름 (0.8점)
                    if user_info and user_info.get('name'):
                        case_conditions.append("WHEN experience_text LIKE %s THEN 0.8")
                        case_params.append(f"%{user_info['name']}%")
                    
                    case_conditions.append("ELSE 0.5")
                    case_sql = " ".join(case_conditions)
                    
                    cursor.execute(f"""
                        SELECT id, experience_text, experience_date, 
                               CASE {case_sql}
                               END as relevance_score
                        FROM user_experiences
                        WHERE user_id = %s AND ({all_conditions})
                        ORDER BY relevance_score DESC, created_at DESC
                        LIMIT %s
                    """, case_params + keyword_params + [user_id, top_k])
                else:
                    # 키워드가 없으면 사용자 정보 기반으로 최근 경험들 반환 (생년월일/시간 최우선)
                    if user_info and (user_info.get('name') or user_info.get('birth_date') or user_info.get('birth_time')):
                        user_conditions = []
                        user_params = []
                        case_conditions = []
                        case_params = []
                        
                        # 1순위: 생년월일 관련 키워드
                        birth_keywords = self.extract_birth_date_keywords(user_info)
                        for birth_keyword in birth_keywords:
                            user_conditions.append("experience_text LIKE %s")
                            user_params.append(f"%{birth_keyword}%")
                            case_conditions.append("WHEN experience_text LIKE %s THEN 1.0")
                            case_params.append(f"%{birth_keyword}%")
                        
                        # 2순위: 태어난 시간 관련 키워드
                        time_keywords = self.extract_birth_time_keywords(user_info)
                        for time_keyword in time_keywords:
                            user_conditions.append("experience_text LIKE %s")
                            user_params.append(f"%{time_keyword}%")
                            case_conditions.append("WHEN experience_text LIKE %s THEN 0.9")
                            case_params.append(f"%{time_keyword}%")
                        
                        # 3순위: 사용자 이름
                        if user_info.get('name'):
                            user_conditions.append("experience_text LIKE %s")
                            user_params.append(f"%{user_info['name']}%")
                            case_conditions.append("WHEN experience_text LIKE %s THEN 0.8")
                            case_params.append(f"%{user_info['name']}%")
                        
                        case_conditions.append("ELSE 0.5")
                        case_sql = " ".join(case_conditions)
                        
                        cursor.execute(f"""
                            SELECT id, experience_text, experience_date, 
                                   CASE {case_sql}
                                   END as relevance_score
                            FROM user_experiences
                            WHERE user_id = %s AND ({' OR '.join(user_conditions)})
                            ORDER BY relevance_score DESC, created_at DESC
                            LIMIT %s
                        """, case_params + [user_id] + user_params + [top_k])
                    else:
                        cursor.execute("""
                            SELECT id, experience_text, experience_date, 0.3 as relevance_score
                            FROM user_experiences
                            WHERE user_id = %s
                            ORDER BY created_at DESC
                            LIMIT %s
                        """, (user_id, top_k))
                
                experiences = cursor.fetchall()
            
            connection.close()
            
            # 결과를 기존 형식에 맞게 변환
            results = []
            for exp in experiences:
                results.append({
                    'experience': {
                        'id': exp['id'],
                        'experience_text': exp['experience_text'],
                        'experience_date': exp['experience_date']
                    },
                    'similarity': exp['relevance_score']
                })
            
            return results
            
        except Exception as e:
            print(f"경험 검색 오류: {e}")
            return []
    
    def get_user_basic_info(self, user_id):
        """사용자의 기본 정보를 조회합니다."""
        try:
            connection = self.get_db_connection()
            if not connection:
                return None
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 사용자 기본 정보 조회
                cursor.execute("""
                    SELECT u.name, u.birth_date, u.birth_time, u.message,
                           p.occupation, p.financial_status, p.interests, 
                           p.personality_traits, p.relationship_status
                    FROM users u
                    LEFT JOIN user_profiles p ON u.id = p.user_id
                    WHERE u.id = %s
                """, (user_id,))
                
                user_info = cursor.fetchone()
            
            connection.close()
            return user_info
            
        except Exception as e:
            print(f"사용자 정보 조회 오류: {e}")
            return None

    def find_similar_users(self, user_id, max_similar=5):
        """유사한 사용자들을 찾습니다 (생년월일, 시간, 이름 기반)."""
        try:
            connection = self.get_db_connection()
            if not connection:
                return []
            
            # 현재 사용자 정보 조회
            current_user = self.get_user_basic_info(user_id)
            if not current_user:
                return []
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                similar_users = []
                
                # 1. 같은 생년월일을 가진 사용자들 (최우선)
                cursor.execute("""
                    SELECT u.id, u.name, u.birth_date, u.birth_time, u.message,
                           p.occupation, p.financial_status, p.interests, 
                           p.current_challenges, p.goals, p.personality_traits, 
                           p.relationship_status, p.health_concerns
                    FROM users u
                    LEFT JOIN user_profiles p ON u.id = p.user_id
                    WHERE u.id != %s AND u.birth_date = %s
                    ORDER BY ABS(TIME_TO_SEC(TIMEDIFF(u.birth_time, %s))) ASC
                    LIMIT %s
                """, (user_id, current_user['birth_date'], current_user['birth_time'], max_similar))
                
                same_birthday_users = cursor.fetchall()
                for user in same_birthday_users:
                    user['similarity_type'] = 'same_birthday'
                    user['similarity_score'] = 1.0
                    similar_users.append(user)
                
                # 2. 같은 월일을 가진 사용자들 (2순위)
                if len(similar_users) < max_similar:
                    current_month = current_user['birth_date'].month
                    current_day = current_user['birth_date'].day
                    
                    cursor.execute("""
                        SELECT u.id, u.name, u.birth_date, u.birth_time, u.message,
                               p.occupation, p.financial_status, p.interests, 
                               p.current_challenges, p.goals, p.personality_traits, 
                               p.relationship_status, p.health_concerns
                        FROM users u
                        LEFT JOIN user_profiles p ON u.id = p.user_id
                        WHERE u.id != %s AND MONTH(u.birth_date) = %s AND DAY(u.birth_date) = %s
                        ORDER BY ABS(TIME_TO_SEC(TIMEDIFF(u.birth_time, %s))) ASC
                        LIMIT %s
                    """, (user_id, current_month, current_day, current_user['birth_time'], max_similar - len(similar_users)))
                    
                    same_monthday_users = cursor.fetchall()
                    for user in same_monthday_users:
                        user['similarity_type'] = 'same_monthday'
                        user['similarity_score'] = 0.8
                        similar_users.append(user)
                
                # 3. 비슷한 시간대를 가진 사용자들 (3순위)
                if len(similar_users) < max_similar:
                    current_time = current_user['birth_time']
                    # 2시간 이내의 시간대
                    cursor.execute("""
                        SELECT u.id, u.name, u.birth_date, u.birth_time, u.message,
                               p.occupation, p.financial_status, p.interests, 
                               p.current_challenges, p.goals, p.personality_traits, 
                               p.relationship_status, p.health_concerns
                        FROM users u
                        LEFT JOIN user_profiles p ON u.id = p.user_id
                        WHERE u.id != %s AND ABS(TIME_TO_SEC(TIMEDIFF(u.birth_time, %s))) <= 7200
                        ORDER BY ABS(TIME_TO_SEC(TIMEDIFF(u.birth_time, %s))) ASC
                        LIMIT %s
                    """, (user_id, current_time, current_time, max_similar - len(similar_users)))
                    
                    similar_time_users = cursor.fetchall()
                    for user in similar_time_users:
                        user['similarity_type'] = 'similar_time'
                        user['similarity_score'] = 0.6
                        similar_users.append(user)
                
                # 4. 비슷한 이름을 가진 사용자들 (4순위)
                if len(similar_users) < max_similar:
                    current_name = current_user['name']
                    # 이름의 첫 글자가 같은 사용자들
                    if len(current_name) > 0:
                        first_char = current_name[0]
                        cursor.execute("""
                            SELECT u.id, u.name, u.birth_date, u.birth_time, u.message,
                                   p.occupation, p.financial_status, p.interests, 
                                   p.current_challenges, p.goals, p.personality_traits, 
                                   p.relationship_status, p.health_concerns
                            FROM users u
                            LEFT JOIN user_profiles p ON u.id = p.user_id
                            WHERE u.id != %s AND u.name LIKE %s
                            ORDER BY u.created_at DESC
                            LIMIT %s
                        """, (user_id, f"{first_char}%", max_similar - len(similar_users)))
                        
                        similar_name_users = cursor.fetchall()
                        for user in similar_name_users:
                            user['similarity_type'] = 'similar_name'
                            user['similarity_score'] = 0.4
                            similar_users.append(user)
            
            connection.close()
            return similar_users[:max_similar]
            
        except Exception as e:
            print(f"유사한 사용자 검색 오류: {e}")
            return []

    def get_similar_users_context(self, user_id, max_similar=3):
        """유사한 사용자들의 컨텍스트를 생성합니다."""
        try:
            similar_users = self.find_similar_users(user_id, max_similar)
            if not similar_users:
                return ""
            
            context_parts = []
            context_parts.append("=== 유사한 사용자들의 데이터 참고 ===")
            
            for i, user in enumerate(similar_users, 1):
                similarity_type_map = {
                    'same_birthday': '같은 생년월일',
                    'same_monthday': '같은 월일',
                    'similar_time': '비슷한 시간대',
                    'similar_name': '비슷한 이름'
                }
                
                similarity_desc = similarity_type_map.get(user['similarity_type'], '유사')
                score = user['similarity_score']
                
                user_context = f"""
{i}. {user['name']} ({similarity_desc}, 유사도: {score:.1f})
   - 생년월일: {user['birth_date']} {user['birth_time']}
   - 직업: {user.get('occupation', '미입력')}
   - 재정상태: {user.get('financial_status', '미입력')}
   - 현재 고민: {user.get('current_challenges', '미입력')}
   - 건강관심사: {user.get('health_concerns', '미입력')}
   - 관심분야: {user.get('interests', '미입력')}
   - 목표: {user.get('goals', '미입력')}
   - 성격특성: {user.get('personality_traits', '미입력')}
   - 연애상태: {user.get('relationship_status', '미입력')}
   - 메시지: {user.get('message', '미입력')}
"""
                context_parts.append(user_context)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"유사한 사용자 컨텍스트 생성 오류: {e}")
            return ""

    def extract_keywords_with_user_context(self, text, user_info):
        """사용자 정보를 고려하여 텍스트에서 키워드를 추출합니다 (생년월일/시간 우선)."""
        keywords = []
        text_lower = text.lower()
        
        # 사용자 정보 기반 키워드 추가 (생년월일/시간 최우선)
        if user_info:
            # 1순위: 생년월일 관련 키워드 추가
            birth_keywords = self.extract_birth_date_keywords(user_info)
            for birth_keyword in birth_keywords:
                if birth_keyword in text_lower:
                    keywords.append(birth_keyword)
            
            # 2순위: 태어난 시간 관련 키워드 추가
            birth_time_keywords = self.extract_birth_time_keywords(user_info)
            for time_keyword in birth_time_keywords:
                if time_keyword in text_lower:
                    keywords.append(time_keyword)
            
            # 3순위: 사용자 이름
            if user_info.get('name') and user_info['name'] in text_lower:
                keywords.append(user_info['name'])
        
        # 기본 키워드들 (최소한만 유지)
        essential_keywords = ['건강', '가족', '친구', '고민', '목표', '계획']
        for keyword in essential_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # 2글자 이상의 단어들도 키워드로 추가 (제한적으로)
        words = re.findall(r'\b\w{2,}\b', text)
        keywords.extend(words[:3])  # 최대 3개까지로 제한
        
        return list(set(keywords))  # 중복 제거

    def extract_birth_date_keywords(self, user_info):
        """생년월일을 기반으로 키워드를 추출합니다."""
        keywords = []
        if not user_info or not user_info.get('birth_date'):
            return keywords
        
        try:
            from datetime import datetime
            birth_date = datetime.strptime(str(user_info['birth_date']), '%Y-%m-%d')
            month = birth_date.month
            day = birth_date.day
            year = birth_date.year
            
            # 계절별 키워드
            if month in [12, 1, 2]:
                keywords.extend(['겨울', '추위', '눈', '크리스마스', '새해'])
            elif month in [3, 4, 5]:
                keywords.extend(['봄', '꽃', '새싹', '따뜻함', '개화'])
            elif month in [6, 7, 8]:
                keywords.extend(['여름', '더위', '휴가', '바다', '수영'])
            elif month in [9, 10, 11]:
                keywords.extend(['가을', '단풍', '수확', '시원함', '독서'])
            
            # 월별 특성 키워드
            month_keywords = {
                1: ['새해', '결심', '목표', '시작'],
                2: ['설날', '가족', '전통', '추위'],
                3: ['봄', '입학', '새출발', '희망'],
                4: ['봄', '꽃', '신록', '활동'],
                5: ['가정의달', '어버이', '가족', '따뜻함'],
                6: ['여름', '시작', '활동', '에너지'],
                7: ['여름', '휴가', '여행', '자유'],
                8: ['여름', '휴가', '바다', '산'],
                9: ['가을', '입학', '학습', '성장'],
                10: ['가을', '단풍', '수확', '감사'],
                11: ['가을', '마무리', '준비', '성찰'],
                12: ['겨울', '크리스마스', '마무리', '회고']
            }
            
            if month in month_keywords:
                keywords.extend(month_keywords[month])
            
            # 생년대별 키워드
            if year >= 1990 and year < 2000:
                keywords.extend(['90년대', '밀레니엄', '젊은세대', '디지털'])
            elif year >= 2000 and year < 2010:
                keywords.extend(['2000년대', '신세대', 'IT', '글로벌'])
            elif year >= 2010:
                keywords.extend(['2010년대', '최신세대', '스마트', 'SNS'])
            
            return keywords
            
        except Exception as e:
            print(f"생년월일 키워드 추출 오류: {e}")
            return []

    def extract_birth_time_keywords(self, user_info):
        """태어난 시간을 기반으로 키워드를 추출합니다."""
        keywords = []
        if not user_info or not user_info.get('birth_time'):
            return keywords
        
        try:
            from datetime import datetime
            birth_time = datetime.strptime(str(user_info['birth_time']), '%H:%M:%S').time()
            hour = birth_time.hour
            
            # 시간대별 특성 키워드
            if 0 <= hour < 6:
                keywords.extend(['새벽', '밤', '고요함', '깊은생각', '영감', '독서'])
            elif 6 <= hour < 12:
                keywords.extend(['아침', '활기', '에너지', '새출발', '운동', '활동'])
            elif 12 <= hour < 18:
                keywords.extend(['오후', '활동', '사교', '업무', '소통', '협력'])
            elif 18 <= hour < 24:
                keywords.extend(['저녁', '휴식', '가족', '친구', '여가', '문화'])
            
            # 구체적인 시간대별 키워드
            time_keywords = {
                0: ['자정', '새벽', '고요함', '깊은생각'],
                1: ['새벽', '밤', '고요함', '영감'],
                2: ['새벽', '밤', '고요함', '깊은생각'],
                3: ['새벽', '밤', '고요함', '영감'],
                4: ['새벽', '밤', '고요함', '깊은생각'],
                5: ['새벽', '아침', '새출발', '활기'],
                6: ['아침', '새출발', '활기', '운동'],
                7: ['아침', '활기', '에너지', '새출발'],
                8: ['아침', '활기', '에너지', '업무'],
                9: ['아침', '활기', '에너지', '업무'],
                10: ['오전', '활동', '업무', '에너지'],
                11: ['오전', '활동', '업무', '에너지'],
                12: ['정오', '점심', '활동', '사교'],
                13: ['오후', '활동', '업무', '에너지'],
                14: ['오후', '활동', '업무', '소통'],
                15: ['오후', '활동', '업무', '소통'],
                16: ['오후', '활동', '업무', '마무리'],
                17: ['오후', '활동', '마무리', '휴식'],
                18: ['저녁', '휴식', '가족', '친구'],
                19: ['저녁', '휴식', '가족', '친구'],
                20: ['저녁', '휴식', '가족', '여가'],
                21: ['저녁', '휴식', '가족', '문화'],
                22: ['밤', '휴식', '가족', '여가'],
                23: ['밤', '휴식', '고요함', '여가']
            }
            
            if hour in time_keywords:
                keywords.extend(time_keywords[hour])
            
            return keywords
            
        except Exception as e:
            print(f"태어난 시간 키워드 추출 오류: {e}")
            return []

    def extract_keywords(self, text):
        """텍스트에서 키워드를 추출합니다."""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 처리가 필요)
        keywords = []
        
        # 일반적인 키워드들
        common_keywords = ['직업', '돈', '재정', '사랑', '연애', '건강', '가족', '친구', '공부', '일', '취업', '이직', '결혼', '이혼', '여행', '취미', '운동', '음식', '스트레스', '고민', '목표', '계획', '미래', '과거', '현재']
        
        text_lower = text.lower()
        for keyword in common_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # 2글자 이상의 단어들도 키워드로 추가
        words = re.findall(r'\b\w{2,}\b', text)
        keywords.extend(words[:5])  # 최대 5개까지
        
        return list(set(keywords))  # 중복 제거
    
    def get_personalized_advice(self, user_id, query_text):
        """사용자의 과거 경험과 개인 정보를 바탕으로 개인화된 조언을 제공합니다."""
        try:
            # 사용자 기본 정보 조회
            user_info = self.get_user_basic_info(user_id)
            
            # 유사한 경험 검색
            similar_experiences = self.search_similar_experiences(user_id, query_text, top_k=3)
            
            # 사용자 정보 기반 컨텍스트 생성
            user_context = self.create_user_context_for_advice(user_info)
            
            if not similar_experiences and not user_context:
                return "아직 관련된 경험 데이터가 없습니다. 더 많은 경험을 공유해주세요."
            
            # 과거 경험들을 바탕으로 조언 생성
            experience_context = ""
            if similar_experiences:
                for i, sim_exp in enumerate(similar_experiences, 1):
                    exp = sim_exp['experience']
                    similarity = sim_exp['similarity']
                    experience_context += f"{i}. {exp['experience_text']} (관련도: {similarity:.2f})\n"
            
            # 과거 경험 컨텍스트 생성
            experience_section = ""
            if experience_context:
                experience_section = f"사용자의 과거 유사한 경험들:\n{experience_context}"
            
            advice_prompt = f"""
            사용자의 질문: {query_text}
            
            {user_context}
            
            {experience_section}
            
            위의 사용자 정보와 과거 경험들을 바탕으로 사용자에게 개인화된 조언을 제공해주세요.
            사용자의 직업, 성격, 관심사 등을 고려하여 구체적이고 실용적인 조언을 포함해주세요.
            """
            
            return advice_prompt
            
        except Exception as e:
            print(f"개인화된 조언 생성 오류: {e}")
            return "개인화된 조언을 생성하는 중 오류가 발생했습니다."
    
    def create_user_context_for_advice(self, user_info):
        """조언 생성을 위한 사용자 컨텍스트를 생성합니다."""
        if not user_info:
            return ""
        
        context_parts = []
        
        # 기본 정보
        if user_info.get('name'):
            context_parts.append(f"이름: {user_info['name']}")
        
        if user_info.get('birth_date'):
            context_parts.append(f"생년월일: {user_info['birth_date']}")
        
        if user_info.get('birth_time'):
            context_parts.append(f"태어난 시간: {user_info['birth_time']}")
        
        # 직업 및 재정 상태
        if user_info.get('occupation'):
            context_parts.append(f"직업: {user_info['occupation']}")
        
        if user_info.get('financial_status'):
            context_parts.append(f"재정상태: {user_info['financial_status']}")
        
        # 성격 및 관심사
        if user_info.get('personality_traits'):
            context_parts.append(f"성격특성: {user_info['personality_traits']}")
        
        if user_info.get('interests'):
            context_parts.append(f"관심분야: {user_info['interests']}")
        
        # 관계 상태
        if user_info.get('relationship_status'):
            context_parts.append(f"연애상태: {user_info['relationship_status']}")
        
        # 현재 상황
        if user_info.get('message'):
            context_parts.append(f"현재 상황/메시지: {user_info['message']}")
        
            if context_parts:
                return "=== 사용자 정보 ===\n" + "\n".join(context_parts) + "\n"
        
        return ""
    
    def get_user_context_for_fortune(self, user_id):
        """사주 분석을 위한 사용자 컨텍스트를 생성합니다."""
        try:
            connection = self.get_db_connection()
            if not connection:
                return ""
            
            context_parts = []
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 1. 사용자 기본 정보 + 프로필 정보
                cursor.execute("""
                    SELECT u.name, u.birth_date, u.birth_time, u.message,
                           p.financial_status, p.occupation, p.interests, 
                           p.current_challenges, p.goals, p.personality_traits, 
                           p.relationship_status, p.health_concerns
                    FROM users u
                    LEFT JOIN user_profiles p ON u.id = p.user_id
                    WHERE u.id = %s
                """, (user_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    # 기본 정보
                    basic_info = f"""
=== 사용자 기본 정보 ===
이름: {user_data.get('name', '미입력')}
생년월일: {user_data.get('birth_date', '미입력')}
태어난 시간: {user_data.get('birth_time', '미입력')}
현재 상황/메시지: {user_data.get('message', '미입력')}
"""
                    context_parts.append(basic_info)
                    
                    # 프로필 정보
                    profile_context = f"""
=== 사용자 현재 상황 ===
재정상태: {user_data.get('financial_status', '미입력')}
직업: {user_data.get('occupation', '미입력')}
관심분야: {user_data.get('interests', '미입력')}
현재 고민: {user_data.get('current_challenges', '미입력')}
목표: {user_data.get('goals', '미입력')}
성격특성: {user_data.get('personality_traits', '미입력')}
연애상태: {user_data.get('relationship_status', '미입력')}
건강관심사: {user_data.get('health_concerns', '미입력')}
"""
                    context_parts.append(profile_context)
                
                # 2. 최근 경험들 (최근 5개)
                cursor.execute("""
                    SELECT experience_text, experience_date, created_at
                    FROM user_experiences
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (user_id,))
                experiences = cursor.fetchall()
                
                if experiences:
                    experience_context = "\n=== 최근 경험들 ===\n"
                    for i, exp in enumerate(experiences, 1):
                        experience_context += f"{i}. {exp['experience_text']}\n"
                    context_parts.append(experience_context)
                
                # 3. 과거 사주 분석 결과들 (최근 3개)
                cursor.execute("""
                    SELECT analysis_result, created_at
                    FROM fortune_analysis
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (user_id,))
                past_analyses = cursor.fetchall()
                
                if past_analyses:
                    analysis_context = "\n=== 과거 사주 분석 요약 ===\n"
                    for i, analysis in enumerate(past_analyses, 1):
                        # 분석 결과의 첫 200자만 요약
                        summary = analysis['analysis_result'][:200] + "..." if len(analysis['analysis_result']) > 200 else analysis['analysis_result']
                        analysis_context += f"{i}. {summary}\n"
                    context_parts.append(analysis_context)
            
            connection.close()
            
            # 4. 유사한 사용자들의 데이터 추가 (RAG 참고용)
            similar_users_context = self.get_similar_users_context(user_id, max_similar=3)
            if similar_users_context:
                context_parts.append(similar_users_context)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"사용자 컨텍스트 생성 오류: {e}")
            return ""
    
    def save_fortune_analysis_context(self, user_id, analysis_result, context_type="fortune_analysis"):
        """사주 분석 결과를 RAG 컨텍스트로 저장합니다."""
        try:
            connection = self.get_db_connection()
            if not connection:
                return False
            
            with connection.cursor() as cursor:
                # 사주 분석 결과를 경험 데이터로도 저장하여 RAG에서 활용
                cursor.execute("""
                    INSERT INTO user_experiences (user_id, experience_text, experience_date)
                    VALUES (%s, %s, %s)
                """, (
                    user_id,
                    f"[사주분석] {analysis_result[:500]}...",  # 처음 500자만 저장
                    datetime.now().date()
                ))
                connection.commit()
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"사주 분석 컨텍스트 저장 오류: {e}")
            return False
