-- 사주 & RAG 시스템 데이터베이스 생성 (한자 처리 최적화)
CREATE DATABASE IF NOT EXISTS user_info_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 데이터베이스 사용
USE user_info_db;

-- 사용자 정보 테이블 생성 (한자 이름 처리 최적화)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '이름 (한자)',
    birth_date DATE NOT NULL COMMENT '생년월일',
    birth_time TIME NOT NULL COMMENT '태어난 시간',
    message TEXT NOT NULL COMMENT '할말',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보 테이블';

-- 사용자 프로필 테이블 생성 (RAG용 개인화 데이터)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 프로필 테이블';

-- 사주 분석 결과 테이블 생성
CREATE TABLE IF NOT EXISTS fortune_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '사용자 ID',
    analysis_result TEXT NOT NULL COMMENT '사주 분석 결과',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사주 분석 결과 테이블';

-- 사용자 경험 데이터 테이블 생성 (RAG용)
CREATE TABLE IF NOT EXISTS user_experiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '사용자 ID',
    experience_text TEXT NOT NULL COMMENT '경험 내용',
    experience_date DATE COMMENT '경험 날짜',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 경험 데이터 테이블';

-- 한자 처리를 위한 인덱스 추가
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_birth_date ON users(birth_date);
CREATE INDEX idx_users_birth_time ON users(birth_time);

-- 샘플 데이터 삽입 (한자 이름 테스트용)
INSERT INTO users (name, birth_date, birth_time, message) VALUES
('洪吉東', '1990-01-01', '09:30:00', '직업은 의사입니다. 좋은일이 있었습니다.'),
('金哲洙', '1985-05-15', '14:20:00', '직업은 간호사입니다. 좋은일이 있었습니다.'),
('李英姬', '1992-12-25', '22:45:00', '직업은 프로그래머 입니다. 안좋은일이있었습니다'),
('朴信厚', '2003-06-03', '19:00:00', '오얏나무에 관심이 있습니다.'),
('安英旰', '1995-03-15', '11:30:00', '한자 이름으로 사주를 보고 싶습니다.');

-- 샘플 프로필 데이터 삽입
INSERT INTO user_profiles (user_id, financial_status, occupation, interests, current_challenges, goals, personality_traits, relationship_status, health_concerns) VALUES
(1, '좋음', '의사', '의학, 독서, 여행', '환자 치료에 대한 부담감', '전문의가 되고 싶음', '책임감 강함, 신중함', '기혼', '스트레스 관리'),
(2, '보통', '간호사', '건강관리, 운동', '야간 근무로 인한 피로', '대학원 진학', '친화력 좋음, 인내심 강함', '연애중', '수면 패턴 개선'),
(3, '어려움', '프로그래머', '코딩, 게임', '취업 준비', '좋은 회사 취업', '완벽주의, 호기심 많음', '미혼', '안구건조증'),
(4, '보통', '학생', '오얏나무, 원예, 자연', '학업 부담', '원예 전문가가 되고 싶음', '조용함, 집중력 좋음', '미혼', '알레르기'),
(5, '좋음', '회사원', '사주, 명리학, 한자', '진로 고민', '사주 전문가가 되고 싶음', '신중함, 분석적', '연애중', '없음');

-- 샘플 경험 데이터 삽입
INSERT INTO user_experiences (user_id, experience_text, experience_date) VALUES
(1, '오늘 환자를 성공적으로 치료했습니다. 보람을 느꼈습니다.', '2024-01-15'),
(1, '새로운 의료 기술을 배웠습니다. 앞으로 더 나은 치료를 할 수 있을 것 같습니다.', '2024-01-20'),
(2, '야간 근무가 힘들었지만 환자들이 회복하는 모습을 보니 뿌듯했습니다.', '2024-01-18'),
(2, '동료들과 좋은 관계를 유지하고 있습니다. 팀워크가 중요하다는 것을 깨달았습니다.', '2024-01-22'),
(3, '코딩 테스트에서 좋은 성과를 거두었습니다. 자신감이 생겼습니다.', '2024-01-16'),
(3, '새로운 프로그래밍 언어를 배우기 시작했습니다. 도전이지만 흥미롭습니다.', '2024-01-25'),
(4, '오얏나무를 키우기 시작했습니다. 자연과 함께하는 시간이 좋습니다.', '2024-01-20'),
(4, '원예 관련 책을 읽고 있습니다. 식물에 대해 더 많이 알고 싶습니다.', '2024-01-25'),
(5, '한자 공부를 시작했습니다. 사주 분석에 도움이 될 것 같습니다.', '2024-01-18'),
(5, '명리학 서적을 읽고 있습니다. 전통 문화에 관심이 생겼습니다.', '2024-01-22');