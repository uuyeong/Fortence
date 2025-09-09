import google.generativeai as genai
from config import GEMINI_API_KEY
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import time
import re
from saju_calculator import SajuCalculator

class FortuneAnalyzer:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.saju_calculator = SajuCalculator()
    
    def _search_hanja_strokes(self, char):
        """개별 한자의 획수를 인터넷에서 검색합니다"""
        try:
            # 방법 1: 한자사전 사이트 검색
            strokes = self._search_from_hanja_dict(char)
            if strokes:
                return strokes
            
            # 방법 2: 네이버 한자사전 검색
            strokes = self._search_from_naver(char)
            if strokes:
                return strokes
            
            # 방법 3: 구글 검색
            strokes = self._search_from_google(char)
            if strokes:
                return strokes
            
            # 모든 방법 실패 시 기본값
            return 8
            
        except Exception as e:
            print(f"한자 '{char}' 검색 중 오류: {e}")
            return 8
    
    def _search_from_hanja_dict(self, char):
        """한자사전 사이트에서 획수 검색"""
        try:
            # 한자사전 사이트 URL (예시)
            url = f"https://hanja.dict.naver.com/search?query={char}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 획수 정보를 찾는 패턴들
                stroke_patterns = [
                    r'(\d+)획',
                    r'획수[:\s]*(\d+)',
                    r'총[:\s]*(\d+)[:\s]*획'
                ]
                
                for pattern in stroke_patterns:
                    matches = re.findall(pattern, soup.get_text())
                    if matches:
                        return int(matches[0])
            
            return None
            
        except Exception:
            return None
    
    def _search_from_naver(self, char):
        """네이버에서 한자 획수 검색"""
        try:
            # 네이버 검색 URL
            search_query = f"{char} 한자 획수"
            url = f"https://search.naver.com/search.naver?query={search_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 획수 정보를 찾는 패턴들
                stroke_patterns = [
                    r'(\d+)획',
                    r'총[:\s]*(\d+)[:\s]*획',
                    r'획수[:\s]*(\d+)'
                ]
                
                for pattern in stroke_patterns:
                    matches = re.findall(pattern, soup.get_text())
                    if matches:
                        return int(matches[0])
            
            return None
            
        except Exception:
            return None
    
    def _search_from_google(self, char):
        """구글에서 한자 획수 검색"""
        try:
            # 구글 검색 URL
            search_query = f"{char} 한자 획수"
            url = f"https://www.google.com/search?q={search_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 획수 정보를 찾는 패턴들
                stroke_patterns = [
                    r'(\d+)획',
                    r'총[:\s]*(\d+)[:\s]*획',
                    r'획수[:\s]*(\d+)'
                ]
                
                for pattern in stroke_patterns:
                    matches = re.findall(pattern, soup.get_text())
                    if matches:
                        return int(matches[0])
            
            return None
            
        except Exception:
            return None
    
    def calculate_hanja_strokes(self, name):
        """인터넷 검색을 통해 한자 이름의 총 획수를 계산합니다"""
        total_strokes = 0
        
        for char in name:
            try:
                # 한자 획수 검색을 위한 여러 방법 시도
                strokes = self._search_hanja_strokes(char)
                total_strokes += strokes
                print(f"한자 '{char}' 획수: {strokes}")
            except Exception as e:
                print(f"한자 '{char}' 획수 검색 실패: {e}")
                # 검색 실패 시 기본값 사용
                total_strokes += 8
        
        return total_strokes
    
    def analyze_fortune(self, name, birth_date, birth_time, message="", profile_data=None, user_id=None, rag_context=""):
        """
        생년월일시와 사용자 프로필, RAG 컨텍스트를 기반으로 사주를 분석합니다.
        """
        try:
            # 생년월일시를 한국어로 변환 (시간 형식 처리)
            # birth_time이 "HH:MM:SS" 또는 "HH:MM" 형식일 수 있음
            if len(birth_time.split(':')) == 3:
                # "HH:MM:SS" 형식
                birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
            else:
                # "HH:MM" 형식
                birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
            
            # 프로필 정보를 포함한 프롬프트 생성
            profile_context = ""
            if profile_data:
                profile_context = f"""
            === 사용자 현재 상황 ===
            재정상태: {profile_data.get('financial_status', '미입력')}
            직업: {profile_data.get('occupation', '미입력')}
            관심분야: {profile_data.get('interests', '미입력')}
            현재 고민: {profile_data.get('current_challenges', '미입력')}
            목표: {profile_data.get('goals', '미입력')}
            성격특성: {profile_data.get('personality_traits', '미입력')}
            연애상태: {profile_data.get('relationship_status', '미입력')}
            건강관심사: {profile_data.get('health_concerns', '미입력')}
            """
            
            # RAG 컨텍스트 추가 (유사한 사용자 데이터 포함)
            rag_context_section = ""
            if rag_context:
                rag_context_section = f"""
            === 과거 데이터 및 유사한 사용자 데이터 기반 개인화 정보 ===
            {rag_context}
            """
            
            # 한자 이름 획수 계산 (인터넷 검색 방식)
            name_strokes = self.calculate_hanja_strokes(name)
            
            # 사주팔자 계산
            saju_result = self.saju_calculator.calculate_saju(birth_date, birth_time)
            saju_analysis = self.saju_calculator.get_detailed_analysis(saju_result)
            
            # 사주 분석을 위한 프롬프트 생성
            prompt = f"""
            다음 정보를 바탕으로 개인화된 사주를 분석해주세요:

            === 기본 정보 ===
            이름 (한자): {name} (총 {name_strokes}획)
            생년월일시: {birth_datetime.strftime('%Y년 %m월 %d일 %H시 %M분')}
            추가 메시지: {message}
            {profile_context}
            {rag_context_section}

            === 계산된 사주팔자 ===
            {saju_analysis}

            === 분석 요청사항 ===
            위의 계산된 사주팔자, 한자 이름 획수, 현재 상황, 과거 데이터를 종합하여 다음 항목들을 분석해주세요:
            우선 하고싶은 말을 토대로 사주를 요약해서 답변해줘
            1. 계산된 사주팔자 (년주, 월주, 일주, 시주) 상세 해석 - 한자 이름의 획수와 오행도 고려
            2. 오행 분석 (금, 목, 수, 화, 토) - 계산된 오행 분포와 이름의 한자 종합 분석
            3. 계산된 사주팔자 (년주, 월주, 일주, 시주)로 살에 대한 분석도 해줘 살에 대한 분석은 가능하면 모두 해줘 
            4. 십이지지와 천간 분석 - 계산된 사주팔자 기반
            5. 성격 특성 (사주팔자와 현재 상황, 과거 경험을 연관지어)
            6. 운세 및 조언 (개인화된 조언)
            7. 직업운 (현재 직업과 목표, 과거 경험 고려, 사주팔자 고려, 살 고려)
            8. 연애운 (현재 관계상태와 과거 경험 고려, 사주팔자 고려, 살 고려)
            9. 건강운 (건강관심사와 과거 경험 고려, 사주팔자 고려, 살 고려)
            10. 금전운 (재정상태와 과거 경험 고려, 사주팔자 고려, 살 고려)
            11. 올해 내년 말년의 운세 (현재 고민, 목표, 과거 패턴 고려, 사주팔자 고려, 살 고려)

            === 분석 지침 ===
            - 한국 전통 사주학에 기반하여 분석하되, 현대적이고 실용적인 관점에서 해석
            - **한자 이름의 획수({name_strokes}획)와 오행을 고려하여 더 정확한 사주 분석 제공**
            - **한자 이름의 의미와 음양오행을 분석에 포함**
            - 검색에 기반해서 하는 식으로 해줘
            - 사용자의 현재 상황, 고민, 과거 경험을 모두 반영한 개인화된 조언 제공
            - 과거 사주 분석 결과와의 연관성도 고려하여 일관성 있는 조언 제공
            - **유사한 사용자들의 데이터를 참고하여 더 정확한 분석 제공**
            - **같은 생년월일/시간/이름을 가진 사람들의 경험과 패턴을 분석에 활용**
            - **유사한 사용자들의 직업, 재정상태, 고민, 건강관심사 등을 참고하여 조언**
            - 꼭 긍정적인 말만 하지않고 부정적인 말도해줘 그렇다고 부정적인 말만하지는 말고 조화롭게 얘기해줘
            - 각 항목을 구체적이고 실행 가능한 조언으로 작성
            - 과거 데이터와 유사한 사용자 데이터에서 발견된 패턴이나 경향을 활용하여 더 정확한 예측 제공
            
            === 출력 형식 지침 ===
            - 각 항목은 반드시 "번호. 제목" 형태로 시작해야 합니다 (예: "1. 계산된 사주팔자 상세 해석")
            - 내용 중간에 빈 줄이 있어도 괜찮지만, 각 항목은 명확히 구분되어야 합니다
            - 단어를 '**' 로 강조하는 표현을 절대 쓰지 말아라
            - 마크다운 문법이나 특수 기호는 사용하지 말고 순수한 텍스트로만 작성해주세요
            - 1.계산된 사주팔자 상세 해석 의 경우에는 줄글보다는 좀 더 한눈에 알아보기 쉽게 출력해줘 
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"사주 분석 오류: {e}")
            return f"사주 분석 중 오류가 발생했습니다: {str(e)}"
    
