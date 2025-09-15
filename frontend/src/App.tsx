import React, { useState } from 'react';
import UserInfoForm from './components/UserInfoForm';
import FortuneAnalysis from './components/FortuneAnalysis';
import './App.css';

function App() {
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [userName, setUserName] = useState<string>('');
  const [showFortune, setShowFortune] = useState(false);

  // 사용자 정보 저장 후 사주 분석 표시
  const handleUserSubmit = (userId: number, name: string) => {
    setCurrentUserId(userId);
    setUserName(name);
    setShowFortune(true); // 사주 분석 결과 표시
  };

  // 새로운 분석을 위해 초기화
  const handleNewAnalysis = () => {
    setCurrentUserId(null);
    setUserName('');
    setShowFortune(false);
  };

  return (
    <div 
      className={`App ${showFortune ? 'fortune-page' : 'user-page'}`}
    >
      <div className="app-header">
        <h1 className="app-title">Fortence</h1>
        {userName && (
          <div className="user-info">
            <button onClick={handleNewAnalysis} className="new-analysis-btn">
              새로운 분석하기
            </button>
          </div>
        )}
      </div>

      {/* 프로젝트 소개 섹션 */}
      {!showFortune && (
        <div className="project-intro">
          <div className="intro-container">
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">📊</div>
                <h3>통계 기반 RAG 시스템</h3>
                <p>사용자 데이터를 통계적으로 분석하여 더욱 정확하고 개인화된 사주 해석을 제공합니다.</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🗄️</div>
                <h3>SQL 데이터 관리</h3>
                <p>체계적인 데이터베이스 구조로 사용자 정보를 안전하게 관리하고 빠른 검색을 지원합니다.</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🤖</div>
                <h3>AI 자연어처리</h3>
                <p>Google Gemini AI를 활용한 고도화된 자연어처리로 더욱 정밀한 사주 분석과 조언을 제공합니다.</p>
              </div>
            </div>
            <div className="github-link">
              <a href="https://github.com/uuyeong/Fortence" target="_blank" rel="noopener noreferrer" className="github-btn">
                <span className="github-icon"></span>
                GitHub 바로가기
              </a>
            </div>
          </div>
        </div>
      )}

      <div className="app-content">
        {!showFortune ? (
          <UserInfoForm onUserSubmit={handleUserSubmit} />
        ) : (
          <FortuneAnalysis userId={currentUserId} />
        )}
      </div>
    </div>
  );
}

export default App;
