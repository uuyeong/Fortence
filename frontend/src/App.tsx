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
