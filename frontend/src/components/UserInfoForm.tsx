import React, { useState } from 'react';
import axios from 'axios';
import './UserInfoForm.css';

interface UserInfo {
  name: string;
  birthDate: string;
  birthTime: string;
  message: string;
  // 프로필 정보 추가
  financialStatus: string;
  occupation: string;
  interests: string;
  currentChallenges: string;
  goals: string;
  personalityTraits: string;
  relationshipStatus: string;
  healthConcerns: string;
}

interface UserInfoFormProps {
  onUserSubmit: (userId: number, name: string) => void;
}

const UserInfoForm: React.FC<UserInfoFormProps> = ({ onUserSubmit }) => {
  const [formData, setFormData] = useState<UserInfo>({
    name: '',
    birthDate: '',
    birthTime: '',
    message: '',
    financialStatus: '',
    occupation: '',
    interests: '',
    currentChallenges: '',
    goals: '',
    personalityTraits: '',
    relationshipStatus: '',
    healthConcerns: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // 이름 필드의 경우 한자만 허용 (확장된 한자 범위)
    if (name === 'name') {
      // 한자 범위 확장: 기본 한자(U+4E00~U+9FFF) + 확장 한자(U+3400~U+4DBF) + 호환 한자(U+F900~U+FAFF)
      const cleanedValue = value.replace(/[^\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]/g, '');
      setFormData(prev => ({
        ...prev,
        [name]: cleanedValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      // 1. 사용자 기본 정보 저장
      const userResponse = await axios.post('http://localhost:5000/api/users', {
        name: formData.name,
        birthDate: formData.birthDate,
        birthTime: formData.birthTime,
        message: formData.message
      });
      
      const userId = userResponse.data.user_id;
      
      // 2. 사용자 프로필 저장
      await axios.post('http://localhost:5000/api/profile', {
        userId: userId,
        financialStatus: formData.financialStatus,
        occupation: formData.occupation,
        interests: formData.interests,
        currentChallenges: formData.currentChallenges,
        goals: formData.goals,
        personalityTraits: formData.personalityTraits,
        relationshipStatus: formData.relationshipStatus,
        healthConcerns: formData.healthConcerns
      });
      
      console.log('데이터 전송 성공:', userResponse.data);
      setSubmitStatus('success');
      
      // 사용자 정보 저장 완료 후 사주 분석으로 이동
      onUserSubmit(userId, formData.name);
      
      setFormData({
        name: '',
        birthDate: '',
        birthTime: '',
        message: '',
        financialStatus: '',
        occupation: '',
        interests: '',
        currentChallenges: '',
        goals: '',
        personalityTraits: '',
        relationshipStatus: '',
        healthConcerns: ''
      });
    } catch (error) {
      console.error('데이터 전송 실패:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="user-info-form-container">
      <h1>사용자 정보 입력</h1>
      <form onSubmit={handleSubmit} className="user-info-form">
        <div className="form-group">
          <label htmlFor="name">이름 (한자):</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            placeholder="한자 이름만 입력하세요 (예: 金哲洙)"
          />
          <small className="form-help">
            ⚠️ 한자만 입력해주세요. 한글이 섞이면 사주 분석이 부정확할 수 있습니다.<br/>
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="birthDate">생년월일 (양력):</label>
          <input
            type="date"
            id="birthDate"
            name="birthDate"
            value={formData.birthDate}
            onChange={handleInputChange}
            required
          />
          <small className="form-help">
            📅 양력 생년월일을 입력해주세요. 자동으로 음력으로 변환한 후 음력 기준으로 사주를 계산합니다.
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="birthTime">태어난 시간:</label>
          <input
            type="time"
            id="birthTime"
            name="birthTime"
            value={formData.birthTime}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="message">특별히 궁금한점:</label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleInputChange}
            required
            placeholder="하고 싶은 말을 입력하세요"
            rows={4}
          />
        </div>

        {/* 프로필 정보 섹션 */}
        <div className="profile-section">
          <h2>📋 개인 프로필 (필수사항)</h2>
          <p className="profile-description">
            더 정확한 사주 분석을 위해 현재 상황을 알려주세요.
          </p>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="financialStatus">재정 상태:</label>
              <select
                id="financialStatus"
                name="financialStatus"
                value={formData.financialStatus}
                onChange={handleInputChange}
              >
                <option value="">선택하세요</option>
                <option value="매우 좋음">매우 좋음</option>
                <option value="좋음">좋음</option>
                <option value="보통">보통</option>
                <option value="어려움">어려움</option>
                <option value="매우 어려움">매우 어려움</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="occupation">직업:</label>
              <input
                type="text"
                id="occupation"
                name="occupation"
                value={formData.occupation}
                onChange={handleInputChange}
                placeholder="현재 직업을 입력하세요"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="interests">관심 분야:</label>
            <textarea
              id="interests"
              name="interests"
              value={formData.interests}
              onChange={handleInputChange}
              placeholder="관심 있는 분야나 취미를 입력하세요"
              rows={2}
            />
          </div>

          <div className="form-group">
            <label htmlFor="currentChallenges">현재 고민이나 어려움:</label>
            <textarea
              id="currentChallenges"
              name="currentChallenges"
              value={formData.currentChallenges}
              onChange={handleInputChange}
              placeholder="현재 겪고 있는 고민이나 어려움을 입력하세요"
              rows={2}
            />
          </div>

          <div className="form-group">
            <label htmlFor="goals">목표나 계획:</label>
            <textarea
              id="goals"
              name="goals"
              value={formData.goals}
              onChange={handleInputChange}
              placeholder="현재 목표나 향후 계획을 입력하세요"
              rows={2}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="personalityTraits">성격 특성:</label>
              <input
                type="text"
                id="personalityTraits"
                name="personalityTraits"
                value={formData.personalityTraits}
                onChange={handleInputChange}
                placeholder="자신의 성격이나 특성을 입력하세요"
              />
            </div>

            <div className="form-group">
              <label htmlFor="relationshipStatus">연애/결혼 상태:</label>
              <select
                id="relationshipStatus"
                name="relationshipStatus"
                value={formData.relationshipStatus}
                onChange={handleInputChange}
              >
                <option value="">선택하세요</option>
                <option value="미혼">미혼</option>
                <option value="연애중">연애중</option>
                <option value="기혼">기혼</option>
                <option value="이혼">이혼</option>
                <option value="상태공개안함">상태공개안함</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="healthConcerns">건강 관심사:</label>
            <textarea
              id="healthConcerns"
              name="healthConcerns"
              value={formData.healthConcerns}
              onChange={handleInputChange}
              placeholder="건강 관련 관심사나 주의사항을 입력하세요"
              rows={2}
            />
          </div>
        </div>

        <button 
          type="submit" 
          disabled={isSubmitting}
          className="submit-button"
        >
          {isSubmitting ? '전송 중...' : '제출하기'}
        </button>

        {submitStatus === 'success' && (
          <div className="success-message">
            <h3>✅ 정보가 성공적으로 저장되었습니다!</h3>
            <p>🔮 사주 분석이 자동으로 시작됩니다...</p>
            <p>잠시만 기다려주세요.</p>
          </div>
        )}

        {submitStatus === 'error' && (
          <div className="error-message">
            오류가 발생했습니다. 다시 시도해주세요.
          </div>
        )}
      </form>
    </div>
  );
};

export default UserInfoForm;
