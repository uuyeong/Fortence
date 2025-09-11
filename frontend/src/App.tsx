import React, { useState } from 'react';
import UserInfoForm from './components/UserInfoForm';
import FortuneAnalysis from './components/FortuneAnalysis';
import './App.css';

function App() {
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [userName, setUserName] = useState<string>('');
  const [showFortune, setShowFortune] = useState(false);
  const [backgroundImage, setBackgroundImage] = useState<string>('background_1.jpg');

  // 사용자 정보 저장 후 사주 분석 표시
  const handleUserSubmit = (userId: number, name: string) => {
    setCurrentUserId(userId);
    setUserName(name);
    setShowFortune(true); // 사주 분석 결과 표시
    setBackgroundImage('background_2.jpg'); // 배경 이미지 변경
  };

  // 새로운 분석을 위해 초기화
  const handleNewAnalysis = () => {
    setCurrentUserId(null);
    setUserName('');
    setShowFortune(false);
    setBackgroundImage('background_1.jpg'); // 원래 배경으로 복원
  };

  return (
    <div 
      className="App" 
      style={{ 
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center bottom',
        backgroundRepeat: 'no-repeat',
        transition: 'background-image 0.5s ease-in-out'
      }}
    >
      <div className="app-header">
        <img 
          src="/vector_title.png" 
          alt="Fortence Title" 
          className="title-vector-image"
        />
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
