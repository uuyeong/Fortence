import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl, API_CONFIG } from '../config';
import './FortuneAnalysis.css';

interface FortuneData {
  name: string;
  birthDate: string;
  birthTime: string;
  message: string;
  userId?: number;
}

interface AnalysisResult {
  analysis: string;
}

interface FortuneAnalysisProps {
  userId: number | null;
}

const FortuneAnalysis: React.FC<FortuneAnalysisProps> = ({ userId }) => {
  const [fortuneData, setFortuneData] = useState<FortuneData>({
    name: '',
    birthDate: '',
    birthTime: '',
    message: '',
    userId: userId || undefined
  });
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [autoAnalysisTriggered, setAutoAnalysisTriggered] = useState(false);

  // 사용자 정보를 가져와서 자동으로 사주 분석 실행
  useEffect(() => {
    const fetchUserDataAndAnalyze = async () => {
      if (userId && !autoAnalysisTriggered) {
        console.log('사용자 ID:', userId); // 디버깅용
        try {
          // 사용자 정보 가져오기
          const userResponse = await axios.get(`${getApiUrl(API_CONFIG.ENDPOINTS.USERS)}/${userId}`);
          console.log('API 응답:', userResponse); // 디버깅용
          const userData = userResponse.data;
          
          console.log('사용자 정보:', userData); // 디버깅용
          
          if (userData && userData.name) {
            // fortuneData 업데이트
            setFortuneData({
              name: userData.name,
              birthDate: userData.birth_date,
              birthTime: userData.birth_time,
              message: userData.message || '',
              userId: userId
            });
            
            // 자동 사주 분석 실행
            setAutoAnalysisTriggered(true);
            await handleFortuneAnalysis({
              name: userData.name,
              birthDate: userData.birth_date,
              birthTime: userData.birth_time,
              message: userData.message || '',
              userId: userId
            }, true); // 자동 분석임을 표시
          } else {
            console.log('사용자 데이터가 없습니다.');
            setFortuneData(prev => ({
              ...prev,
              name: '데이터 없음',
              birthDate: '데이터 없음',
              birthTime: '데이터 없음',
              message: '사용자 데이터를 찾을 수 없습니다.'
            }));
          }
          
        } catch (error) {
          console.error('사용자 정보 가져오기 실패:', error);
          // TypeScript 오류 해결을 위한 타입 가드
          if (error && typeof error === 'object' && 'response' in error) {
            const axiosError = error as any;
            console.error('오류 상세:', axiosError.response?.data);
          }
          // 오류 발생 시 기본값으로 설정
          setFortuneData(prev => ({
            ...prev,
            name: 'API 오류',
            birthDate: 'API 오류',
            birthTime: 'API 오류',
            message: '서버 연결에 실패했습니다.'
          }));
        }
      }
    };

    fetchUserDataAndAnalyze();
  }, [userId, autoAnalysisTriggered]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFortuneData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFortuneAnalysis = async (data?: FortuneData, isAutoAnalysis: boolean = false) => {
    // 자동 분석이 아닌 경우에만 중복 실행 방지
    if (!isAutoAnalysis && isAnalyzing) {
      return;
    }
    
    setIsAnalyzing(true);
    try {
      const analysisData = data || fortuneData;
      const response = await axios.post(getApiUrl(API_CONFIG.ENDPOINTS.FORTUNE_ANALYZE), analysisData);
      setAnalysisResult({
        analysis: response.data.analysis
      });
    } catch (error) {
      console.error('사주 분석 오류:', error);
      alert('사주 분석 중 오류가 발생했습니다.');
    } finally {
      setIsAnalyzing(false);
    }
  };


  const handleAnalysis = () => {
    handleFortuneAnalysis();
  };

  // 분석 결과를 파싱하여 각 항목별로 분리하는 함수
  const parseAnalysisResult = (analysisText: string) => {
    const sections = [];
    const lines = analysisText.split('\n');
    let currentSection = null;
    let currentContent = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // 번호와 제목을 찾는 패턴들 (다양한 형태 지원)
      const titlePatterns = [
        /^(\d+)\.\s*(.+?):?\s*$/,  // 1. 제목:
        /^\*\*(\d+)\.\s*(.+?):?\*\*/,  // **1. 제목:**
        /^(\d+)\.\s*\*\*(.+?)\*\*/,  // 1. **제목**
        /^(\d+)\.\s*(.+?)$/  // 1. 제목 (콜론 없음)
      ];
      
      let titleMatch = null;
      for (const pattern of titlePatterns) {
        titleMatch = line.match(pattern);
        if (titleMatch) break;
      }
      
      if (titleMatch) {
        // 이전 섹션이 있다면 저장
        if (currentSection) {
          sections.push({
            number: currentSection.number,
            title: currentSection.title,
            content: currentContent.join('\n').trim()
          });
        }
        
        // 새로운 섹션 시작
        currentSection = {
          number: titleMatch[1],
          title: titleMatch[2].replace(/[:\*\s]*$/, '').trim() // 끝의 콜론, 별표, 공백 제거
        };
        currentContent = [];
      } else if (currentSection && line) {
        // 현재 섹션의 내용 추가 (빈 줄이 아닌 경우만)
        currentContent.push(line);
      }
    }

    // 마지막 섹션 저장
    if (currentSection) {
      sections.push({
        number: currentSection.number,
        title: currentSection.title,
        content: currentContent.join('\n').trim()
      });
    }

    return sections;
  };

  // 사용자 정보가 없는 경우 안내 메시지 표시
  if (!userId) {
    return (
      <div className="fortune-analysis-container">
        <div className="login-required">
          <h2>📝 사용자 정보를 먼저 입력해주세요</h2>
          <p>사주 분석을 위해서는 사용자 정보가 필요합니다.</p>
          <p>위에서 정보를 입력하시면 자동으로 사주 분석이 시작됩니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fortune-analysis-container">
      <h1>🔮 사주 분석</h1>
      
      {autoAnalysisTriggered && (
        <div className="auto-analysis-notice">
          <h3>✨ 자동 사주 분석 시작!</h3>
          <p>입력하신 정보를 바탕으로 사주 분석을 진행하고 있습니다.</p>
        </div>
      )}
      

      <div className="form-container">
        <div className="user-info-display">
          <h3>📋 사용자 정보</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">이름:</span>
              <span className="info-value">{fortuneData.name || '정보 없음'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">생년월일:</span>
              <span className="info-value">{fortuneData.birthDate || '정보 없음'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">생시:</span>
              <span className="info-value">{fortuneData.birthTime || '정보 없음'}</span>
            </div>
            {fortuneData.message && (
              <div className="info-item">
                <span className="info-label">추가 궁금한점:</span>
                <span className="info-value">{fortuneData.message}</span>
              </div>
            )}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="message">추가 메시지 (선택사항):</label>
          <textarea
            id="message"
            name="message"
            value={fortuneData.message}
            onChange={handleInputChange}
            placeholder="궁금한 점이나 특별한 질문이 있다면 입력하세요"
            rows={3}
          />
        </div>

        <button 
          onClick={handleAnalysis}
          disabled={isAnalyzing || !fortuneData.name || !fortuneData.birthDate || !fortuneData.birthTime}
          className="analyze-button"
        >
          {isAnalyzing ? '분석 중...' : '사주 분석하기'}
        </button>
        
        <div className="analysis-note">
          <p>💡 사용자 정보는 자동으로 로드되었습니다. 추가 메시지만 입력하시면 됩니다.</p>
        </div>
      </div>

      {analysisResult && (
        <div className="result-container">
          <h2>📊 사주 분석 결과</h2>
          <div className="analysis-sections">
            {parseAnalysisResult(analysisResult.analysis).map((section, index) => (
              <div key={index} className="analysis-section">
                <h3 className="section-title">
                  <span className="section-number">{section.number}.</span>
                  <span className="section-title-text">{section.title}</span>
                </h3>
                <div className="section-content">
                  {section.content.split('\n').map((line, lineIndex) => (
                    <p key={lineIndex}>{line}</p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FortuneAnalysis;
