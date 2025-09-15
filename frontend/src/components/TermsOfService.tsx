import React from 'react';
import './TermsOfService.css';

interface TermsOfServiceProps {
  onBack: () => void;
}

const TermsOfService: React.FC<TermsOfServiceProps> = ({ onBack }) => {
  return (
    <div className="terms-container">
      <div className="terms-header">
        <button onClick={onBack} className="back-button">
          ← 돌아가기
        </button>
        <h1>개인정보 수집 및 이용 동의</h1>
      </div>
      
      <div className="terms-content">
        <div className="terms-section">
          <h2>1. 개인정보 수집 및 이용 목적</h2>
          <p>
            Fortence는 사주 분석 서비스를 제공하기 위해 다음과 같은 개인정보를 수집하고 이용합니다.
          </p>
          <ul>
            <li><strong>이름:</strong> 개인화된 사주 분석 결과에 이름을 포함하여 더욱 친근하고 개인적인 서비스 제공</li>
            <li><strong>생년월일 및 출생시간:</strong> 정확한 사주 계산 및 운세 분석을 위한 필수 정보</li>
            <li><strong>개인 메시지 및 프로필 정보:</strong> 사용자의 현재 상황과 고민을 반영한 맞춤형 분석 및 조언 제공</li>
          </ul>
        </div>

        <div className="terms-section">
          <h2>2. 수집하는 개인정보 항목</h2>
          <p>필수 수집 항목:</p>
          <ul>
            <li>이름</li>
            <li>생년월일 (양력 기준, 자동 음력 변환)</li>
            <li>출생시간</li>
            <li>개인 메시지</li>
            <li>재정 상태, 직업, 관심분야, 현재 고민, 목표, 성격특성, 연애/결혼 상태, 건강 관심사</li>
          </ul>
        </div>

        <div className="terms-section">
          <h2>3. 개인정보 보유 및 이용 기간</h2>
          <p>
            수집된 개인정보는 서비스 개선 및 분석을 위해 보관됩니다. 
            사용자들의 데이터를 분석하여 사주 해석의 정확도와 품질을 지속적으로 향상시키는 목적으로 사용됩니다.
          </p>
          <p>
            <strong>중요:</strong> 수집된 개인정보는 오직 Fortence 서비스 개선 목적으로만 사용되며, 
            제3자와 공유하거나 외부로 유출하지 않습니다. 관련 법령에 의해 보존이 필요한 경우에는 해당 기간 동안 보관합니다.
          </p>
        </div>

        <div className="terms-section">
          <h2>4. 개인정보 처리 위탁</h2>
          <p>
            Fortence는 원활한 서비스 제공을 위해 다음과 같이 개인정보 처리 업무를 위탁하고 있습니다.
          </p>
          <ul>
            <li><strong>수탁자:</strong> 이두호</li>
            <li><strong>위탁 업무 내용:</strong> 클라우드 서버 관리 및 데이터베이스 운영</li>
            <li><strong>위탁 기간:</strong> 서비스 운영 기간 동안</li>
          </ul>
          <p>
            위탁업무와 관련하여 개인정보가 안전하게 관리될 수 있도록 필요한 사항을 규정하고, 
            수탁자가 개인정보보호법에 따라 안전하게 처리하도록 관리·감독하고 있습니다.
          </p>
        </div>

        <div className="terms-section">
          <h2>5. 개인정보의 안전성 확보 조치</h2>
          <p>
            Fortence는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다:
          </p>
          <ul>
            <li>개인정보 암호화</li>
            <li>해킹 등에 대비한 기술적 대책</li>
            <li>개인정보 처리시스템 등의 접근권한 관리</li>
          </ul>
        </div>

        <div className="terms-section">
          <h2>6. 동의 거부권 및 불이익</h2>
          <p>
            이용자는 개인정보 수집 및 이용에 대한 동의를 거부할 권리가 있습니다. 
            다만, 동의를 거부할 경우 사주 분석 서비스를 이용할 수 없습니다.
          </p>
        </div>

      </div>
    </div>
  );
};

export default TermsOfService;
