// API 설정
const getBaseUrl = (): string => {
  // 환경 변수가 있으면 사용
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // 현재 호스트가 localhost가 아니면 실제 서버 IP 사용
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'http://121.138.24.119:5000';
  }
  
  // 로컬 개발 환경에서는 localhost 사용
  return 'http://localhost:5000';
};

export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  
  // API 엔드포인트들
  ENDPOINTS: {
    USERS: '/api/users',
    PROFILE: '/api/profile',
    FORTUNE_ANALYZE: '/api/fortune/analyze',
    HEALTH: '/api/health'
  }
};

// API URL을 생성하는 헬퍼 함수
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
