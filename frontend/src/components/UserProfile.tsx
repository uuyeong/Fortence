import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserProfile.css';

interface UserProfile {
  userId: number;
  financialStatus: string;
  occupation: string;
  interests: string;
  currentChallenges: string;
  goals: string;
  personalityTraits: string;
  relationshipStatus: string;
  healthConcerns: string;
}

const UserProfile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>({
    userId: 1, // 기본값, 실제로는 로그인한 사용자 ID를 사용
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

  useEffect(() => {
    // 기존 프로필 데이터 로드
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/profile/${profile.userId}`);
      if (response.data.profile) {
        setProfile(prev => ({
          ...prev,
          ...response.data.profile
        }));
      }
    } catch (error) {
      console.log('프로필 로드 실패:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await axios.post('http://localhost:5000/api/profile', profile);
      console.log('프로필 저장 성공:', response.data);
      setSubmitStatus('success');
    } catch (error) {
      console.error('프로필 저장 실패:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="user-profile-container">
      <h1>👤 개인 프로필 설정</h1>
      <p className="profile-description">
        더 정확한 사주 분석을 위해 현재 상황을 알려주세요. 
        이 정보는 개인화된 사주 분석에 활용됩니다.
      </p>

      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-section">
          <h2>💰 재정 상황</h2>
          <div className="form-group">
            <label htmlFor="financialStatus">재정 상태:</label>
            <select
              id="financialStatus"
              name="financialStatus"
              value={profile.financialStatus}
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
        </div>

        <div className="form-section">
          <h2>💼 직업 & 관심사</h2>
          <div className="form-group">
            <label htmlFor="occupation">직업:</label>
            <input
              type="text"
              id="occupation"
              name="occupation"
              value={profile.occupation}
              onChange={handleInputChange}
              placeholder="현재 직업을 입력하세요"
            />
          </div>

          <div className="form-group">
            <label htmlFor="interests">관심 분야:</label>
            <textarea
              id="interests"
              name="interests"
              value={profile.interests}
              onChange={handleInputChange}
              placeholder="관심 있는 분야나 취미를 입력하세요"
              rows={3}
            />
          </div>
        </div>

        <div className="form-section">
          <h2>🎯 현재 상황 & 목표</h2>
          <div className="form-group">
            <label htmlFor="currentChallenges">현재 고민이나 어려움:</label>
            <textarea
              id="currentChallenges"
              name="currentChallenges"
              value={profile.currentChallenges}
              onChange={handleInputChange}
              placeholder="현재 겪고 있는 고민이나 어려움을 입력하세요"
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="goals">목표나 계획:</label>
            <textarea
              id="goals"
              name="goals"
              value={profile.goals}
              onChange={handleInputChange}
              placeholder="현재 목표나 향후 계획을 입력하세요"
              rows={3}
            />
          </div>
        </div>

        <div className="form-section">
          <h2>👤 개인 특성</h2>
          <div className="form-group">
            <label htmlFor="personalityTraits">성격 특성:</label>
            <textarea
              id="personalityTraits"
              name="personalityTraits"
              value={profile.personalityTraits}
              onChange={handleInputChange}
              placeholder="자신의 성격이나 특성을 입력하세요"
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="relationshipStatus">연애/결혼 상태:</label>
            <select
              id="relationshipStatus"
              name="relationshipStatus"
              value={profile.relationshipStatus}
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

        <div className="form-section">
          <h2>🏥 건강 & 기타</h2>
          <div className="form-group">
            <label htmlFor="healthConcerns">건강 관심사:</label>
            <textarea
              id="healthConcerns"
              name="healthConcerns"
              value={profile.healthConcerns}
              onChange={handleInputChange}
              placeholder="건강 관련 관심사나 주의사항을 입력하세요"
              rows={3}
            />
          </div>
        </div>

        <button 
          type="submit" 
          disabled={isSubmitting}
          className="submit-button"
        >
          {isSubmitting ? '저장 중...' : '프로필 저장하기'}
        </button>

        {submitStatus === 'success' && (
          <div className="success-message">
            프로필이 성공적으로 저장되었습니다! 이제 더 정확한 사주 분석을 받을 수 있습니다.
          </div>
        )}

        {submitStatus === 'error' && (
          <div className="error-message">
            프로필 저장 중 오류가 발생했습니다. 다시 시도해주세요.
          </div>
        )}
      </form>
    </div>
  );
};

export default UserProfile;
