from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Tuple, Optional

class SajuCalculator:
    """사주팔자(연주, 월주, 일주, 시주) 계산 클래스"""
    
    def __init__(self):
        # 천간 (10개) - 한자
        self.CHEONGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        
        # 지지 (12개) - 한자
        self.JIJI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 기준일: 1900년 1월 1일 (甲戌일 - 원래 설정으로 복원)
        self.BASE_DATE = datetime(1900, 1, 1)
        self.BASE_JIAZI_INDEX = 10   # 甲戌 (60갑자 순환표에서 11번째, 인덱스는 10)
        
        # 60갑자 순환표 데이터
        self.JIAZI_CYCLE = [
            '甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉',
            '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未',
            '甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳',
            '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯',
            '甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑',
            '甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'
        ]
        
        # 절기 데이터 (양력 기준) - 표에 맞게 정확히 수정
        self.SOLAR_TERMS = {
            1: [6],        # 소한 (1/6)
            2: [4],        # 입춘 (2/4)
            3: [6],        # 경칩 (3/6)
            4: [5],        # 청명 (4/5)
            5: [6],        # 입하 (5/6)
            6: [6],        # 망종 (6/6)
            7: [7],        # 소서 (7/7)
            8: [7],        # 입추 (8/7)
            9: [7],        # 백로 (9/7)
            10: [8],       # 한로 (10/8)
            11: [7],       # 입동 (11/7)
            12: [7]        # 대설 (12/7)
        }
        
        # 월지 계산을 위한 절기 매핑 (표 기준)
        self.MONTH_JIJI_MAPPING = {
            1: '丑',   # 소한(1/6)~입춘(2/4) 전
            2: '寅',   # 입춘(2/4)~경칩(3/6) 전
            3: '卯',   # 경칩(3/6)~청명(4/5) 전
            4: '辰',   # 청명(4/5)~입하(5/6) 전
            5: '巳',   # 입하(5/6)~망종(6/6) 전
            6: '午',   # 망종(6/6)~소서(7/7) 전
            7: '未',   # 소서(7/7)~입추(8/7) 전
            8: '申',   # 입추(8/7)~백로(9/7) 전
            9: '酉',   # 백로(9/7)~한로(10/8) 전
            10: '戌',  # 한로(10/8)~입동(11/7) 전
            11: '亥',  # 입동(11/7)~대설(12/7) 전
            12: '子'   # 대설(12/7)~소한(1/6) 전
        }
        
        # 오행 매핑
        self.CHEONGAN_FIVE_ELEMENTS = {
            '甲': '木', '乙': '木',
            '丙': '火', '丁': '火',
            '戊': '土', '己': '土',
            '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }
        
        self.JIJI_FIVE_ELEMENTS = {
            '子': '水', '亥': '水',
            '寅': '木', '卯': '木',
            '辰': '土', '戌': '土', '丑': '土', '未': '土',
            '巳': '火', '午': '火',
            '申': '金', '酉': '金'
        }
        
        # 천간합 매핑
        self.CHEONGAN_COMBINATIONS = {
            ('甲', '己'): '土', ('己', '甲'): '土',
            ('乙', '庚'): '金', ('庚', '乙'): '金',
            ('丙', '辛'): '水', ('辛', '丙'): '水',
            ('丁', '壬'): '木', ('壬', '丁'): '木',
            ('戊', '癸'): '火', ('癸', '戊'): '火'
        }
        
        # 연간에 따른 월간 시작점 매핑 (표 기준)
        self.YEAR_TO_MONTH_START = {
            '甲': '丙', '己': '丙',  # 甲, 己 → 丙寅 시작
            '乙': '戊', '庚': '戊',  # 乙, 庚 → 戊寅 시작
            '丙': '庚', '辛': '庚',  # 丙, 辛 → 庚寅 시작
            '丁': '壬', '壬': '壬',  # 丁, 壬 → 壬寅 시작
            '戊': '甲', '癸': '甲'   # 戊, 癸 → 甲寅 시작
        }
        
        # 일간에 따른 자시 천간 매핑 (표 기준)
        self.DAY_TO_HOUR_START = {
            '甲': '甲', '己': '甲',  # 甲, 己 → 甲子 시작
            '乙': '丙', '庚': '丙',  # 乙, 庚 → 丙子 시작
            '丙': '戊', '辛': '戊',  # 丙, 辛 → 戊子 시작
            '丁': '庚', '壬': '庚',  # 丁, 壬 → 庚子 시작
            '戊': '壬', '癸': '壬'   # 戊, 癸 → 壬子 시작
        }
    
    
    
    def calculate_saju(self, birth_date: str, birth_time: str) -> Dict[str, str]:
        """
        생년월일시를 입력받아 사주팔자를 계산합니다.
        
        Args:
            birth_date: 생년월일 (YYYY-MM-DD 형식)
            birth_time: 생시 (HH:MM 형식)
            
        Returns:
            사주팔자 딕셔너리
        """
        try:
            # 날짜 파싱
            year, month, day = map(int, birth_date.split('-'))
            
            # 시간 파싱 (시간 형식 자동 처리)
            if len(birth_time.split(':')) == 3:
                # HH:MM:SS 형식
                time_parts = birth_time.split(':')
                hour, minute, second = map(int, time_parts)
            else:
                # HH:MM 형식
                time_parts = birth_time.split(':')
                hour, minute = map(int, time_parts)
                second = 0
            
            # 최종 날짜시간 생성
            birth_datetime = datetime(year, month, day, hour, minute, second)
            
            # 연주 계산
            year_pillar = self._calculate_year_pillar(birth_datetime.year)
            
            # 월주 계산
            month_pillar = self._calculate_month_pillar(birth_datetime)
            
            # 일주 계산
            day_pillar = self._calculate_day_pillar(birth_datetime)
            
            # 시주 계산
            hour_pillar = self._calculate_hour_pillar(birth_datetime)
            
            return {
                'year_pillar': year_pillar,      # 연주
                'month_pillar': month_pillar,   # 월주
                'day_pillar': day_pillar,       # 일주
                'hour_pillar': hour_pillar,     # 시주
                'birth_date': birth_date,        # 생년월일
                'birth_time': birth_time         # 생시
            }
            
        except Exception as e:
            print(f"사주 계산 오류: {e}")
            return {}
    
    def _calculate_year_pillar(self, year: int) -> str:
        """연주 계산"""
        # 기준년도(1900년)로부터의 차이 계산
        year_diff = year - 1900
        
        # 천간 계산 (10년 주기) - 1900년은 庚년
        base_cheongan_index = 6  # 庚
        cheongan_index = (base_cheongan_index + year_diff) % 10
        
        # 지지 계산 (12년 주기) - 1900년은 子년
        base_jiji_index = 0  # 子
        jiji_index = (base_jiji_index + year_diff) % 12
        
        return f"{self.CHEONGAN[cheongan_index]}{self.JIJI[jiji_index]}"
    
    def _calculate_month_pillar(self, birth_datetime: datetime) -> str:
        """월주 계산 (절기 기준) - 표에 맞게 정확히 수정"""
        year = birth_datetime.year
        month = birth_datetime.month
        day = birth_datetime.day
        
        # 해당 월의 절기 확인
        solar_term_day = self.SOLAR_TERMS[month][0]
        
        # 절기 이전이면 이전 달의 지지 사용
        if day < solar_term_day:
            month = month - 1 if month > 1 else 12
            if month == 12:
                year -= 1
        
        # 월지 결정
        month_jiji = self.MONTH_JIJI_MAPPING[month]
        
        # 연간 천간 가져오기
        year_cheongan = self._get_year_cheongan(year)
        
        # 연간에 따른 월간 시작점 결정 (표 기준)
        month_start_cheongan = self.YEAR_TO_MONTH_START[year_cheongan]
        
        # 월지 순서 (寅부터 시작)
        jiji_order = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
        
        # 현재 월지의 인덱스 찾기
        month_jiji_index = jiji_order.index(month_jiji)
        
        # 월간 계산: 시작 천간에서 월지 순서만큼 더하기
        start_cheongan_index = self.CHEONGAN.index(month_start_cheongan)
        month_cheongan_index = (start_cheongan_index + month_jiji_index) % 10
        
        return f"{self.CHEONGAN[month_cheongan_index]}{month_jiji}"
    
    def _calculate_day_pillar(self, birth_datetime: datetime) -> str:
        """일주 계산 (60갑자 순환표 기준 - 자시는 다음날로 계산)"""
        hour = birth_datetime.hour
        minute = birth_datetime.minute
        
        # 시간을 분 단위로 변환
        total_minutes = hour * 60 + minute
        
        # 23:30~00:00 시간대인 경우 다음날 기준으로 일주 계산
        if total_minutes >= 1410:  # 23:30~24:00
            # 다음날 기준으로 일주 계산
            next_day = birth_datetime + timedelta(days=1)
            days_diff = (next_day - self.BASE_DATE).days
        else:
            # 현재날 기준으로 일주 계산
            days_diff = (birth_datetime - self.BASE_DATE).days
        
        # 60갑자 순환표 기준으로 일주 계산
        jiazi_index = (self.BASE_JIAZI_INDEX + days_diff) % 60
        
        return self.JIAZI_CYCLE[jiazi_index]
    
    def _calculate_hour_pillar(self, birth_datetime: datetime) -> str:
        """시주 계산 (표 기준 - 자시는 다음날로 계산)"""
        hour = birth_datetime.hour
        minute = birth_datetime.minute
        
        # 시간을 분 단위로 변환
        total_minutes = hour * 60 + minute
        
        # 시지 매핑 (30분 단위 기준 - 표에 맞게 정확히 수정)
        if total_minutes >= 0 and total_minutes <= 90:  # 00:00~01:30
            hour_jiji = '子'  # 朝子
        elif total_minutes >= 91 and total_minutes <= 210:  # 01:31~03:30
            hour_jiji = '丑'
        elif total_minutes >= 211 and total_minutes <= 330:  # 03:31~05:30
            hour_jiji = '寅'
        elif total_minutes >= 331 and total_minutes <= 450:  # 05:31~07:30
            hour_jiji = '卯'
        elif total_minutes >= 451 and total_minutes <= 570:  # 07:31~09:30
            hour_jiji = '辰'
        elif total_minutes >= 571 and total_minutes <= 690:  # 09:31~11:30
            hour_jiji = '巳'
        elif total_minutes >= 691 and total_minutes <= 810:  # 11:31~13:30
            hour_jiji = '午'
        elif total_minutes >= 811 and total_minutes <= 930:  # 13:31~15:30
            hour_jiji = '未'
        elif total_minutes >= 931 and total_minutes <= 1050:  # 15:31~17:30
            hour_jiji = '申'
        elif total_minutes >= 1051 and total_minutes <= 1170:  # 17:31~19:30
            hour_jiji = '酉'
        elif total_minutes >= 1171 and total_minutes <= 1290:  # 19:31~21:30
            hour_jiji = '戌'
        elif total_minutes >= 1291 and total_minutes <= 1410:  # 21:31~23:30
            hour_jiji = '亥'
        elif total_minutes >= 1411:  # 23:31~24:00
            hour_jiji = '子'  # 夜子
        else:
            hour_jiji = '子'  # 기본값
        
        # 자시(子시) 중에서도 23:31~24:00(夜子)만 다음날의 일간 사용
        if hour_jiji == '子' and total_minutes >= 1411:  # 23:31~24:00 (夜子)
            # 다음날의 일간 계산
            next_day = birth_datetime + timedelta(days=1)
            day_cheongan = self._get_day_cheongan(next_day)
        else:
            # 현재날의 일간 사용 (00:01~01:30 포함)
            day_cheongan = self._get_day_cheongan(birth_datetime)
        
        # 일간에 따른 자시 천간 시작점 결정 (표 기준)
        hour_start_cheongan = self.DAY_TO_HOUR_START[day_cheongan]
        
        # 지지 순서 (子부터 시작)
        jiji_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 현재 시지의 인덱스 찾기
        hour_jiji_index = jiji_order.index(hour_jiji)
        
        # 시주 천간 계산: 자시 천간에서 시지 순서만큼 더하기
        start_cheongan_index = self.CHEONGAN.index(hour_start_cheongan)
        hour_cheongan_index = (start_cheongan_index + hour_jiji_index) % 10
        
        return f"{self.CHEONGAN[hour_cheongan_index]}{hour_jiji}"
    
    def _get_year_cheongan(self, year: int) -> str:
        """연도에 해당하는 천간 반환"""
        year_diff = year - 1900
        base_cheongan_index = 6  # 庚
        cheongan_index = (base_cheongan_index + year_diff) % 10
        return self.CHEONGAN[cheongan_index]
    
    def _get_day_cheongan(self, birth_datetime: datetime) -> str:
        """일간 반환 (60갑자 순환표 기준)"""
        days_diff = (birth_datetime - self.BASE_DATE).days
        jiazi_index = (self.BASE_JIAZI_INDEX + days_diff) % 60
        return self.JIAZI_CYCLE[jiazi_index][0]  # 천간 부분만 반환
    
    def analyze_five_elements(self, saju: Dict[str, str]) -> Dict[str, any]:
        """사주팔자의 오행 분석"""
        if not saju:
            return {}
        
        # 각 주의 오행 추출
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        five_elements_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        cheongan_list = []
        
        for pillar in pillars:
            if pillar in saju:
                pillar_value = saju[pillar]
                if len(pillar_value) == 2:
                    cheongan = pillar_value[0]
                    jiji = pillar_value[1]
                    
                    cheongan_list.append(cheongan)
                    
                    # 천간 오행
                    if cheongan in self.CHEONGAN_FIVE_ELEMENTS:
                        five_elements_count[self.CHEONGAN_FIVE_ELEMENTS[cheongan]] += 1
                    
                    # 지지 오행
                    if jiji in self.JIJI_FIVE_ELEMENTS:
                        five_elements_count[self.JIJI_FIVE_ELEMENTS[jiji]] += 1
        
        # 일간 (일주의 천간) 추출
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        day_element = self.CHEONGAN_FIVE_ELEMENTS.get(day_cheongan, '')
        
        # 천간합 분석
        combinations = []
        for i in range(len(cheongan_list)):
            for j in range(i + 1, len(cheongan_list)):
                combo = (cheongan_list[i], cheongan_list[j])
                if combo in self.CHEONGAN_COMBINATIONS:
                    combinations.append({
                        'pair': combo,
                        'result_element': self.CHEONGAN_COMBINATIONS[combo]
                    })
        
        return {
            'day_element': day_element,  # 일간 오행
            'five_elements_count': five_elements_count,
            'strong_elements': [elem for elem, count in five_elements_count.items() if count >= 2],
            'weak_elements': [elem for elem, count in five_elements_count.items() if count == 0],
            'cheongan_combinations': combinations  # 천간합
        }
    
    def get_detailed_analysis(self, saju: Dict[str, str]) -> str:
        """사주팔자 상세 분석 텍스트 생성"""
        if not saju:
            return "사주 계산에 실패했습니다."
        
        five_elements = self.analyze_five_elements(saju)
        
        # 천간합 정보 포맷팅
        combinations_text = ""
        if five_elements.get('cheongan_combinations'):
            combinations_text = "\n天干合: "
            combo_list = []
            for combo in five_elements['cheongan_combinations']:
                pair = combo['pair']
                result = combo['result_element']
                combo_list.append(f"{pair[0]}+{pair[1]}→{result}")
            combinations_text += ", ".join(combo_list)
        
        # 날짜 정보 표시
        date_info = f"""
=== 날짜 정보 ===
생년월일: {saju.get('birth_date', '')}
생시: {saju.get('birth_time', '')}
"""
        
        analysis = f"""
=== 사주팔자 분석 ===
연주: {saju.get('year_pillar', '')} (年柱)
월주: {saju.get('month_pillar', '')} (月柱)
일주: {saju.get('day_pillar', '')} (日柱)
시주: {saju.get('hour_pillar', '')} (時柱){date_info}

=== 五行 분석 ===
일간 五行: {five_elements.get('day_element', '')}
五行 분포: {five_elements.get('five_elements_count', {})}
강한 五行: {', '.join(five_elements.get('strong_elements', []))}
약한 五行: {', '.join(five_elements.get('weak_elements', []))}{combinations_text}
        """
        
        return analysis.strip()

# 사용 예시
if __name__ == "__main__":
    calculator = SajuCalculator()
    
    # 테스트 1: 기본 테스트
    test_date = "1990-05-15"
    test_time = "14:30"
    
    saju = calculator.calculate_saju(test_date, test_time)
    print("사주팔자:", saju)
    
    analysis = calculator.get_detailed_analysis(saju)
    print(analysis)
    
    # 테스트 2: 2002년 9월 20일 (辛卯일 확인)
    test_date2 = "2002-09-20"
    test_time2 = "12:00"
    
    saju2 = calculator.calculate_saju(test_date2, test_time2)
    print(f"\n2002년 9월 20일 일주: {saju2.get('day_pillar', '')}")
    
    # 일주만 계산하는 테스트
    test_datetime = datetime(2002, 9, 20)
    day_pillar = calculator._calculate_day_pillar(test_datetime)
    print(f"직접 계산한 일주: {day_pillar}")
    
    # 테스트 3: 2002년 9월 20일 13시 40분 (乙未 확인)
    test_date3 = "2002-09-20"
    test_time3 = "13:40"
    
    saju3 = calculator.calculate_saju(test_date3, test_time3)
    print(f"\n2002년 9월 20일 13시 40분 시주: {saju3.get('hour_pillar', '')}")
    
    # 시주만 계산하는 테스트
    test_datetime3 = datetime(2002, 9, 20, 13, 40)
    hour_pillar = calculator._calculate_hour_pillar(test_datetime3)
    print(f"직접 계산한 시주: {hour_pillar}")
    
    # 일간 확인
    day_cheongan = calculator._get_day_cheongan(test_datetime3)
    print(f"일간: {day_cheongan}")
    
    # 테스트 4: 다양한 시간대 테스트
    test_times = [
        (0, 0),   # 00:00 - 朝子
        (1, 30),  # 01:30 - 朝子
        (1, 31),  # 01:31 - 丑
        (3, 30),  # 03:30 - 丑
        (3, 31),  # 03:31 - 寅
        (13, 30), # 13:30 - 午
        (13, 31), # 13:31 - 未
        (23, 30), # 23:30 - 亥
        (23, 31), # 23:31 - 夜子
    ]
    
    print(f"\n=== 시간대별 시지 테스트 ===")
    for test_hour, test_minute in test_times:
        test_dt = datetime(2002, 9, 20, test_hour, test_minute)
        hour_pillar = calculator._calculate_hour_pillar(test_dt)
        print(f"{test_hour:02d}:{test_minute:02d} → {hour_pillar}")
