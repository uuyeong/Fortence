from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from saju_calculator import SajuCalculator

class SalCalculator:
    """살(煞) 계산 클래스 - 사주팔자를 기반으로 각종 살을 계산 (fortune_analyzer.py 기준)"""
    
    def __init__(self):
        self.saju_calculator = SajuCalculator()
        
        # 천간 (10개) - 한자
        self.CHEONGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        
        # 지지 (12개) - 한자
        self.JIJI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 천을귀인 매핑 (일간 기준)
        self.CHEONUL_GWIIN = {
            '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
            '乙': ['子', '申'], '己': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '辛': ['午', '寅'],
            '壬': ['巳', '卯'], '癸': ['巳', '卯']
        }
        
        # 문창귀인 매핑 (일간 기준)
        self.MUNCHANG_GWIIN = {
            '甲': ['巳'], '乙': ['午'], '丙': ['申'], '丁': ['酉'], '戊': ['申'],
            '己': ['酉'], '庚': ['亥'], '辛': ['子'], '壬': ['寅'], '癸': ['卯']
        }
        
        # 복성귀인 매핑 (일간 기준)
        self.BOKSEONG_GWIIN = {
            '甲': ['寅'], '乙': ['卯'], '丙': ['子'], '丁': ['酉'], '戊': ['申'],
            '己': ['未'], '庚': ['午'], '辛': ['巳'], '壬': ['辰'], '癸': ['丑']
        }
        
        # 월덕귀인 매핑 (월지 기준 → 천간)
        self.WOLDEOK_GWIIN = {
            '子': '壬', '丑': '庚', '寅': '丙', '卯': '甲', '辰': '壬', '巳': '庚',
            '午': '丙', '未': '甲', '申': '壬', '酉': '庚', '戌': '丙', '亥': '甲'
        }
        
        # 천덕귀인 매핑 (월지 기준 → 천간)
        self.CHEONDEOK_GWIIN = {
            '子': '辛', '丑': '庚', '寅': '丁', '卯': '申', '辰': '乙', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅', '戌': '丙', '亥': '乙'
        }
        
        # 월공귀인 매핑 (월지 기준 → 천간)
        self.WOLGONG_GWIIN = {
            '子': '丙', '丑': '甲', '寅': '壬', '卯': '庚', '辰': '丙', '巳': '甲',
            '午': '壬', '未': '庚', '申': '丙', '酉': '甲', '戌': '壬', '亥': '庚'
        }
        
        # 금여 매핑 (연간 기준)
        self.GEUMYEO = {
            '甲': ['辰'], '乙': ['巳'], '丙': ['未'], '丁': ['申'], '戊': ['未'],
            '己': ['申'], '庚': ['戌'], '辛': ['亥'], '壬': ['丑'], '癸': ['寅']
        }
        
        # 건록 매핑 (일간 기준)
        self.GEONROK = {
            '甲': ['寅'], '乙': ['卯'], '丙': ['巳'], '丁': ['午'], '戊': ['巳'],
            '己': ['午'], '庚': ['申'], '辛': ['酉'], '壬': ['亥'], '癸': ['子']
        }
        
        # 암록 매핑 (일간 기준)
        self.AMROK = {
            '甲': ['亥'], '乙': ['寅'], '丙': ['申'], '丁': ['未'], '戊': ['巳'],
            '己': ['午'], '庚': ['申'], '辛': ['酉'], '壬': ['亥'], '癸': ['寅']
        }
        
        # 삼기 매핑
        self.SAMGI = {
            '천상삼기': ['甲', '戊', '庚'],
            '인간삼기': ['乙', '丙', '丁'],
            '지하삼기': ['辛', '壬', '癸']
        }
        
        # 천의성 매핑 (월지 기준)
        self.CHEONUISEONG = {
            '子': '亥', '丑': '子', '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申', '戌': '酉', '亥': '戌'
        }
        
        # 반안살 매핑 (연지의 삼합 기준)
        self.BANAN_SAL = {
            '寅午戌': '未', '巳酉丑': '戌', '亥卯未': '辰', '申子辰': '丑'
        }
        
        # 양인살 매핑 (일간 기준)
        self.YANGIN_SAL = {
            '甲': ['卯'], '丙': ['午'], '戊': ['午'], '庚': ['酉'], '壬': ['子']
        }
        
        # 도화살 매핑 (삼합 기준)
        self.DOHWA_SAL = {
            '寅午戌': '卯', '申子辰': '酉', '巳酉丑': '午', '亥卯未': '子'
        }
        
        # 역마살 매핑 (삼합 기준)
        self.YEOKMA_SAL = {
            '寅午戌': '申', '申子辰': '寅', '巳酉丑': '亥', '亥卯未': '巳'
        }
        
        # 화개살 매핑 (삼합 기준)
        self.HWAGAE_SAL = {
            '寅午戌': '戌', '申子辰': '辰', '巳酉丑': '丑', '亥卯未': '未'
        }
        
        # 공망살 매핑 (일주 기준)
        self.GONGMANG_SAL = {
            '甲子': ['戌', '亥'], '乙丑': ['戌', '亥'], '丙寅': ['申', '酉'], '丁卯': ['申', '酉'],
            '戊辰': ['午', '未'], '己巳': ['午', '未'], '庚午': ['辰', '巳'], '辛未': ['辰', '巳'],
            '壬申': ['寅', '卯'], '癸酉': ['寅', '卯'], '甲戌': ['申', '酉'], '乙亥': ['申', '酉'],
            '丙子': ['戌', '亥'], '丁丑': ['戌', '亥'], '戊寅': ['子', '丑'], '己卯': ['子', '丑'],
            '庚辰': ['寅', '卯'], '辛巳': ['寅', '卯'], '壬午': ['辰', '巳'], '癸未': ['辰', '巳'],
            '甲申': ['午', '未'], '乙酉': ['午', '未'], '丙戌': ['申', '酉'], '丁亥': ['申', '酉'],
            '戊子': ['戌', '亥'], '己丑': ['戌', '亥'], '庚寅': ['子', '丑'], '辛卯': ['子', '丑'],
            '壬辰': ['寅', '卯'], '癸巳': ['寅', '卯'], '甲午': ['辰', '巳'], '乙未': ['辰', '巳'],
            '丙申': ['午', '未'], '丁酉': ['午', '未'], '戊戌': ['申', '酉'], '己亥': ['申', '酉'],
            '庚子': ['戌', '亥'], '辛丑': ['戌', '亥'], '壬寅': ['子', '丑'], '癸卯': ['子', '丑'],
            '甲辰': ['寅', '卯'], '乙巳': ['寅', '卯'], '丙午': ['辰', '巳'], '丁未': ['辰', '巳'],
            '戊申': ['午', '未'], '己酉': ['午', '未'], '庚戌': ['申', '酉'], '辛亥': ['申', '酉'],
            '壬子': ['戌', '亥'], '癸丑': ['戌', '亥'], '甲寅': ['子', '丑'], '乙卯': ['子', '丑'],
            '丙辰': ['寅', '卯'], '丁巳': ['寅', '卯'], '戊午': ['辰', '巳'], '己未': ['辰', '巳'],
            '庚申': ['午', '未'], '辛酉': ['午', '未'], '壬戌': ['申', '酉'], '癸亥': ['申', '酉']
        }
        
        # 원진살 매핑
        self.WONJIN_SAL = {
            '子': '未', '丑': '午', '寅': '酉', '卯': '申', '辰': '亥', '巳': '戌'
        }
        
        # 귀문관살 매핑
        self.GWIMUNGWAN_SAL = {
            '子': '酉', '丑': '午', '寅': '未', '卯': '申', '辰': '亥', '巳': '戌'
        }
        
        # 백호살 일주
        self.BAEKHO_SAL_ILJU = ['甲辰', '乙未', '丙戌', '丁丑', '戊辰', '壬戌', '癸丑']
        
        # 괴강살 일주
        self.GWAEGANG_SAL_ILJU = ['戊戌', '庚辰', '庚戌', '壬辰']
        
        # 현침살 글자
        self.HYEONCHIM_SAL_CHARS = ['甲', '辛', '卯', '午', '申']
        
        # 홍염살 매핑 (일간 기준)
        self.HONGYEOM_SAL = {
            '甲': ['午'], '乙': ['午'], '丙': ['寅'], '丁': ['未'], '戊': ['辰'],
            '己': ['辰'], '庚': ['戌'], '辛': ['酉'], '壬': ['子'], '癸': ['申']
        }
        
        # 급각살 매핑 (일간 기준)
        self.GEUPGAK_SAL_ILGAN = {
            '甲': ['申'], '乙': ['酉'], '丙': ['亥', '子'], '丁': ['亥', '子'],
            '戊': ['丑', '寅'], '己': ['丑', '寅'], '庚': ['辰'], '辛': ['巳'],
            '壬': ['午', '未'], '癸': ['午', '未']
        }
        
        # 급각살 매핑 (월지 기준)
        self.GEUPGAK_SAL_WOLJI = {
            '寅卯辰': ['戌', '亥'], '巳午未': ['卯', '辰'], 
            '申酉戌': ['寅', '丑'], '亥子丑': ['卯', '辰']
        }
        
        # 겁살 매핑 (삼합 기준)
        self.GEOP_SAL = {
            '申子辰': '巳', '寅午戌': '亥', '亥卯未': '申', '巳酉丑': '寅'
        }
        
        # 수옥살 지지
        self.SUOK_SAL_JIJI = ['辰', '戌', '丑', '未']
        
        # 망신살 매핑 (삼합 기준)
        self.MANGSIN_SAL = {
            '申子辰': '巳', '寅午戌': '亥', '亥卯未': '申', '巳酉丑': '寅'
        }
        
        # 천라지망살 조합
        self.CHEONRA_JIMANG = {
            '천라': ['戌', '亥'], '지망': ['辰', '巳']
        }

    def calculate_sal(self, birth_date: str, birth_time: str) -> Dict[str, any]:
        """
        생년월일시를 입력받아 각종 살(煞)을 계산합니다.
        
        Args:
            birth_date: 생년월일 (YYYY-MM-DD 형식)
            birth_time: 생시 (HH:MM 형식)
            
        Returns:
            살 계산 결과 딕셔너리
        """
        try:
            # 사주팔자 먼저 계산
            saju = self.saju_calculator.calculate_saju(birth_date, birth_time)
            if not saju:
                return {}
            
            # 각종 살 계산
            sal_results = {
                'saju': saju,
                # 길성들
                'cheonul_gwiin': self._calculate_cheonul_gwiin(saju),
                'munchang_gwiin': self._calculate_munchang_gwiin(saju),
                'bokseong_gwiin': self._calculate_bokseong_gwiin(saju),
                'woldeok_gwiin': self._calculate_woldeok_gwiin(saju),
                'cheondeok_gwiin': self._calculate_cheondeok_gwiin(saju),
                'wolgong_gwiin': self._calculate_wolgong_gwiin(saju),
                'geumyeo': self._calculate_geumyeo(saju),
                'geonrok': self._calculate_geonrok(saju),
                'amrok': self._calculate_amrok(saju),
                'samgi': self._calculate_samgi(saju),
                'cheonuiseong': self._calculate_cheonuiseong(saju),
                'banan_sal': self._calculate_banan_sal(saju),
                # 주요 살들
                'dohwa_sal': self._calculate_dohwa_sal(saju),
                'yeokma_sal': self._calculate_yeokma_sal(saju),
                'hwagae_sal': self._calculate_hwagae_sal(saju),
                'gongmang_sal': self._calculate_gongmang_sal(saju),
                # 흉살들
                'yangin_sal': self._calculate_yangin_sal(saju),
                'baekho_sal': self._calculate_baekho_sal(saju),
                'gwaegang_sal': self._calculate_gwaegang_sal(saju),
                'hyeonchim_sal': self._calculate_hyeonchim_sal(saju),
                'hongyeom_sal': self._calculate_hongyeom_sal(saju),
                'geupgak_sal': self._calculate_geupgak_sal(saju),
                'geop_sal': self._calculate_geop_sal(saju),
                'suok_sal': self._calculate_suok_sal(saju),
                'mangsin_sal': self._calculate_mangsin_sal(saju),
                'cheonra_jimang': self._calculate_cheonra_jimang(saju),
                'wonjin_sal': self._calculate_wonjin_sal(saju),
                'gwimungwan_sal': self._calculate_gwimungwan_sal(saju)
            }
            
            return sal_results
            
        except Exception as e:
            print(f"살 계산 오류: {e}")
            return {}

    def _get_samhap_group(self, jiji: str) -> str:
        """지지가 속한 삼합 그룹 반환"""
        samhap_groups = {
            '寅午戌': ['寅', '午', '戌'],
            '申子辰': ['申', '子', '辰'],
            '巳酉丑': ['巳', '酉', '丑'],
            '亥卯未': ['亥', '卯', '未']
        }
        
        for group, jiji_list in samhap_groups.items():
            if jiji in jiji_list:
                return group
        return ''

    def _calculate_cheonul_gwiin(self, saju: Dict[str, str]) -> Dict[str, any]:
        """천을귀인 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.CHEONUL_GWIIN.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_cheonul': len(positions) > 0,
            'description': '옥황상제를 뜻하는 최고의 길신. 좋은 운이 열리고 출세하여 부귀공명을 이룸.'
        }

    def _calculate_munchang_gwiin(self, saju: Dict[str, str]) -> Dict[str, any]:
        """문창귀인 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.MUNCHANG_GWIIN.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_munchang': len(positions) > 0,
            'description': '공부를 잘하며 특히 시험운이 좋음.'
        }

    def _calculate_bokseong_gwiin(self, saju: Dict[str, str]) -> Dict[str, any]:
        """복성귀인 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.BOKSEONG_GWIIN.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_bokseong': len(positions) > 0,
            'description': '인복과 먹을 복이 있어 식의 어려움이 없음.'
        }

    def _calculate_woldeok_gwiin(self, saju: Dict[str, str]) -> Dict[str, any]:
        """월덕귀인 계산"""
        month_jiji = saju.get('month_pillar', '')[1] if saju.get('month_pillar') else ''
        target_cheongan = self.WOLDEOK_GWIIN.get(month_jiji)
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_cheongan = saju.get(pillar, '')[0] if saju.get(pillar) else ''
            if pillar_cheongan == target_cheongan:
                positions.append(pillar_names[i])
        
        return {
            'target_cheongan': target_cheongan,
            'positions': positions,
            'has_woldeok': len(positions) > 0,
            'description': '달의 덕을 입는다는 의미. 명예와 품성이 좋고 공직, 관직에 오르는 데 좋은 기운.'
        }

    def _calculate_cheondeok_gwiin(self, saju: Dict[str, str]) -> Dict[str, any]:
        """천덕귀인 계산"""
        month_jiji = saju.get('month_pillar', '')[1] if saju.get('month_pillar') else ''
        target_cheongan = self.CHEONDEOK_GWIIN.get(month_jiji)
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_cheongan = saju.get(pillar, '')[0] if saju.get(pillar) else ''
            if pillar_cheongan == target_cheongan:
                positions.append(pillar_names[i])
        
        return {
            'target_cheongan': target_cheongan,
            'positions': positions,
            'has_cheondeok': len(positions) > 0,
            'description': '하늘의 덕을 입는다는 의미. 모든 종류의 재난으로부터 자신을 지켜주는 수호천사의 역할.'
        }

    def _calculate_wolgong_gwiin(self, saju: Dict[str, str]) -> Dict[str, any]:
        """월공귀인 계산"""
        month_jiji = saju.get('month_pillar', '')[1] if saju.get('month_pillar') else ''
        target_cheongan = self.WOLGONG_GWIIN.get(month_jiji)
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_cheongan = saju.get(pillar, '')[0] if saju.get(pillar) else ''
            if pillar_cheongan == target_cheongan:
                positions.append(pillar_names[i])
        
        return {
            'target_cheongan': target_cheongan,
            'positions': positions,
            'has_wolgong': len(positions) > 0,
            'description': '하늘에 뜬 달을 의미하며, 타인에게 인기를 얻고 주목받는 기운.'
        }

    def _calculate_geumyeo(self, saju: Dict[str, str]) -> Dict[str, any]:
        """금여 계산"""
        year_cheongan = saju.get('year_pillar', '')[0] if saju.get('year_pillar') else ''
        target_jiji = self.GEUMYEO.get(year_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_geumyeo': len(positions) > 0,
            'description': '배우자운이 좋아 좋은 남편, 아내를 맞이함.'
        }

    def _calculate_geonrok(self, saju: Dict[str, str]) -> Dict[str, any]:
        """건록 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.GEONROK.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_geonrok': len(positions) > 0,
            'description': '평생 굶어죽을 일 없고 의지가 굳으며 건강함. 관직이나 봉급 생활에 유리.'
        }

    def _calculate_amrok(self, saju: Dict[str, str]) -> Dict[str, any]:
        """암록 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.AMROK.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_amrok': len(positions) > 0,
            'description': '남들이 모르는 록(재물, 도움)을 얻음. 위기 시 의외의 도움이 들어옴.'
        }

    def _calculate_samgi(self, saju: Dict[str, str]) -> Dict[str, any]:
        """삼기 계산"""
        # 천간들 추출
        cheongan_list = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        
        for pillar in pillars:
            if saju.get(pillar):
                cheongan_list.append(saju[pillar][0])
        
        found_samgi = []
        
        # 각 삼기 패턴 확인
        for samgi_type, pattern in self.SAMGI.items():
            # 순서대로 확인
            for i in range(len(cheongan_list) - 2):
                if (cheongan_list[i:i+3] == pattern or 
                    cheongan_list[i:i+3] == pattern[::-1]):
                    found_samgi.append({
                        'type': samgi_type,
                        'pattern': cheongan_list[i:i+3],
                        'positions': f'{i+1}-{i+2}-{i+3}번째 기둥'
                    })
        
        return {
            'found_samgi': found_samgi,
            'has_samgi': len(found_samgi) > 0,
            'description': '외모가 좋고 포부가 큼.'
        }

    def _calculate_cheonuiseong(self, saju: Dict[str, str]) -> Dict[str, any]:
        """천의성 계산"""
        month_jiji = saju.get('month_pillar', '')[1] if saju.get('month_pillar') else ''
        target_jiji = self.CHEONUISEONG.get(month_jiji)
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji == target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_cheonuiseong': len(positions) > 0,
            'description': '병에 대한 저항성이 강하며 의료계, 사회복지사 등 활인업에 좋음.'
        }

    def _calculate_banan_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """반안살 계산"""
        year_jiji = saju.get('year_pillar', '')[1] if saju.get('year_pillar') else ''
        samhap_group = self._get_samhap_group(year_jiji)
        target_jiji = self.BANAN_SAL.get(samhap_group)
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji == target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_banan': len(positions) > 0,
            'description': '공을 세우거나 높은 지위에 오를 운.'
        }

    def _calculate_dohwa_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """도화살 계산"""
        year_jiji = saju.get('year_pillar', '')[1] if saju.get('year_pillar') else ''
        day_jiji = saju.get('day_pillar', '')[1] if saju.get('day_pillar') else ''
        
        # 연지 또는 일지 기준으로 삼합 그룹 확인
        samhap_groups = [self._get_samhap_group(year_jiji), self._get_samhap_group(day_jiji)]
        target_jiji_list = []
        
        for group in samhap_groups:
            if group and group in self.DOHWA_SAL:
                target_jiji_list.append(self.DOHWA_SAL[group])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji_list:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': list(set(target_jiji_list)),
            'positions': positions,
            'has_dohwa': len(positions) > 0,
            'description': '색욕을 뜻하는 살. 이성이 끊이지 않으며 유혹에 약함. 긍정적으로는 연예인, 정치인 등 인기 직업에 유리.'
        }

    def _calculate_yeokma_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """역마살 계산"""
        year_jiji = saju.get('year_pillar', '')[1] if saju.get('year_pillar') else ''
        day_jiji = saju.get('day_pillar', '')[1] if saju.get('day_pillar') else ''
        
        # 연지 또는 일지 기준으로 삼합 그룹 확인
        samhap_groups = [self._get_samhap_group(year_jiji), self._get_samhap_group(day_jiji)]
        target_jiji_list = []
        
        for group in samhap_groups:
            if group and group in self.YEOKMA_SAL:
                target_jiji_list.append(self.YEOKMA_SAL[group])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji_list:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': list(set(target_jiji_list)),
            'positions': positions,
            'has_yeokma': len(positions) > 0,
            'description': '한 곳에 정착하지 못하고 떠돌게 되는 살. 현대에는 여행, 해외 활동, 갑작스러운 이직 등에 유리하게 작용.'
        }

    def _calculate_hwagae_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """화개살 계산"""
        year_jiji = saju.get('year_pillar', '')[1] if saju.get('year_pillar') else ''
        day_jiji = saju.get('day_pillar', '')[1] if saju.get('day_pillar') else ''
        
        # 연지 또는 일지 기준으로 삼합 그룹 확인
        samhap_groups = [self._get_samhap_group(year_jiji), self._get_samhap_group(day_jiji)]
        target_jiji_list = []
        
        for group in samhap_groups:
            if group and group in self.HWAGAE_SAL:
                target_jiji_list.append(self.HWAGAE_SAL[group])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji_list:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': list(set(target_jiji_list)),
            'positions': positions,
            'has_hwagae': len(positions) > 0,
            'description': '예술적, 예능적 재능이 있으나 인생에서 인복에 따라 길흉이 크게 달라짐.'
        }

    def _calculate_gongmang_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """공망살 계산"""
        day_pillar = saju.get('day_pillar', '')
        gongmang_jiji = self.GONGMANG_SAL.get(day_pillar, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in gongmang_jiji:
                positions.append({
                    'pillar': pillar_names[i],
                    'jiji': pillar_jiji
                })
        
        return {
            'gongmang_jiji': gongmang_jiji,
            'positions': positions,
            'has_gongmang': len(positions) > 0,
            'description': '모든 노력이 헛되게 되는 살. 길흉의 작용이 무력화됨. 미련살이라고도 함.'
        }

    def _calculate_yangin_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """양인살 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.YANGIN_SAL.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_yangin': len(positions) > 0,
            'description': '강한 기운을 가진 신살. 수술, 교통사고, 사망 등 흉한 작용을 함. 의료계, 법조계 등 생사 관련 직업으로 기운을 상쇄할 수 있음.'
        }

    def _calculate_baekho_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """백호살 계산"""
        day_pillar = saju.get('day_pillar', '')
        has_baekho = day_pillar in self.BAEKHO_SAL_ILJU
        
        return {
            'day_pillar': day_pillar,
            'has_baekho': has_baekho,
            'description': '호랑이에게 물려가는 재앙. 교통사고, 질병, 이별 등 부정적 의미를 가지나 특수 재능을 뜻하기도 함.'
        }

    def _calculate_gwaegang_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """괴강살 계산"""
        day_pillar = saju.get('day_pillar', '')
        has_gwaegang = day_pillar in self.GWAEGANG_SAL_ILJU
        
        return {
            'day_pillar': day_pillar,
            'has_gwaegang': has_gwaegang,
            'description': '극도로 총명하나 폭력적, 파괴적인 힘을 가짐. 극귀(極貴) 또는 극빈(極貧)으로 나타남.'
        }

    def _calculate_hyeonchim_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """현침살 계산"""
        # 사주에서 현침살 글자들 찾기
        found_chars = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_value = saju.get(pillar, '')
            if pillar_value:
                cheongan, jiji = pillar_value[0], pillar_value[1]
                if cheongan in self.HYEONCHIM_SAL_CHARS:
                    found_chars.append({'char': cheongan, 'pillar': pillar_names[i], 'type': '천간'})
                if jiji in self.HYEONCHIM_SAL_CHARS:
                    found_chars.append({'char': jiji, 'pillar': pillar_names[i], 'type': '지지'})
        
        has_hyeonchim = len(found_chars) >= 2
        
        return {
            'found_chars': found_chars,
            'has_hyeonchim': has_hyeonchim,
            'description': '신경이 예민하고 불면증을 겪기 쉬움. 현대에는 의료, 언론, IT 등 직업과 관련.'
        }

    def _calculate_hongyeom_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """홍염살 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        target_jiji = self.HONGYEOM_SAL.get(day_cheongan, [])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_hongyeom': len(positions) > 0,
            'description': '주색에 관한 살. 자신의 주도로 관계를 이끌어감.'
        }

    def _calculate_geupgak_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """급각살 계산"""
        day_cheongan = saju.get('day_pillar', '')[0] if saju.get('day_pillar') else ''
        month_jiji = saju.get('month_pillar', '')[1] if saju.get('month_pillar') else ''
        
        # 일간 기준 급각살
        target_jiji_ilgan = self.GEUPGAK_SAL_ILGAN.get(day_cheongan, [])
        
        # 월지 기준 급각살
        target_jiji_wolji = []
        for season, target_list in self.GEUPGAK_SAL_WOLJI.items():
            if month_jiji in season:
                target_jiji_wolji = target_list
                break
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        all_targets = target_jiji_ilgan + target_jiji_wolji
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in all_targets:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji_ilgan': target_jiji_ilgan,
            'target_jiji_wolji': target_jiji_wolji,
            'positions': positions,
            'has_geupgak': len(positions) > 0,
            'description': '다리를 다치거나 골절상을 입는 사고. 물질적/정신적 기반이 파괴되는 것.'
        }

    def _calculate_geop_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """겁살 계산"""
        day_jiji = saju.get('day_pillar', '')[1] if saju.get('day_pillar') else ''
        samhap_group = self._get_samhap_group(day_jiji)
        target_jiji = self.GEOP_SAL.get(samhap_group)
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji == target_jiji:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': target_jiji,
            'positions': positions,
            'has_geop': len(positions) > 0,
            'description': '남에게 무언가를 뺏기기 쉬움. 외부의 강력한 힘에 의해 결정되는 의미.'
        }

    def _calculate_suok_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """수옥살 계산"""
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in self.SUOK_SAL_JIJI:
                positions.append({
                    'pillar': pillar_names[i],
                    'jiji': pillar_jiji
                })
        
        return {
            'target_jiji': self.SUOK_SAL_JIJI,
            'positions': positions,
            'has_suok': len(positions) > 0,
            'description': '감옥에 갇히거나 자유를 제한 당함.'
        }

    def _calculate_mangsin_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """망신살 계산"""
        year_jiji = saju.get('year_pillar', '')[1] if saju.get('year_pillar') else ''
        day_jiji = saju.get('day_pillar', '')[1] if saju.get('day_pillar') else ''
        
        # 연지 또는 일지 기준으로 삼합 그룹 확인
        samhap_groups = [self._get_samhap_group(year_jiji), self._get_samhap_group(day_jiji)]
        target_jiji_list = []
        
        for group in samhap_groups:
            if group and group in self.MANGSIN_SAL:
                target_jiji_list.append(self.MANGSIN_SAL[group])
        
        positions = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        pillar_names = ['연주', '월주', '일주', '시주']
        
        for i, pillar in enumerate(pillars):
            pillar_jiji = saju.get(pillar, '')[1] if saju.get(pillar) else ''
            if pillar_jiji in target_jiji_list:
                positions.append(pillar_names[i])
        
        return {
            'target_jiji': list(set(target_jiji_list)),
            'positions': positions,
            'has_mangsin': len(positions) > 0,
            'description': '말 그대로 망신을 당함. 공개적인 망신, 재수 없는 일 등이 발생.'
        }

    def _calculate_cheonra_jimang(self, saju: Dict[str, str]) -> Dict[str, any]:
        """천라지망살 계산"""
        # 지지들 추출
        jiji_list = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        
        for pillar in pillars:
            if saju.get(pillar):
                jiji_list.append(saju[pillar][1])
        
        # 천라 확인 (戌과 亥가 함께)
        has_cheonra = '戌' in jiji_list and '亥' in jiji_list
        
        # 지망 확인 (辰과 巳가 함께)
        has_jimang = '辰' in jiji_list and '巳' in jiji_list
        
        return {
            'has_cheonra': has_cheonra,
            'has_jimang': has_jimang,
            'has_cheonra_jimang': has_cheonra or has_jimang,
            'description': '하늘과 땅에 그물이 쳐져 있어 꼼짝하지 못하는 상태. 과거에는 흉살이었으나, 현대에는 종교적 영성이나 내면의 강한 힘으로 재해석되기도 한다.'
        }

    def _calculate_wonjin_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """원진살 계산"""
        # 지지들 추출
        jiji_list = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        
        for pillar in pillars:
            if saju.get(pillar):
                jiji_list.append(saju[pillar][1])
        
        found_pairs = []
        for jiji in jiji_list:
            if jiji in self.WONJIN_SAL:
                target = self.WONJIN_SAL[jiji]
                if target in jiji_list:
                    found_pairs.append(f'{jiji}-{target}')
        
        return {
            'found_pairs': list(set(found_pairs)),
            'has_wonjin': len(found_pairs) > 0,
            'description': '서로 원망하고 화내는 살. 궁합이 좋지 않음.'
        }

    def _calculate_gwimungwan_sal(self, saju: Dict[str, str]) -> Dict[str, any]:
        """귀문관살 계산"""
        # 지지들 추출
        jiji_list = []
        pillars = ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']
        
        for pillar in pillars:
            if saju.get(pillar):
                jiji_list.append(saju[pillar][1])
        
        found_pairs = []
        for jiji in jiji_list:
            if jiji in self.GWIMUNGWAN_SAL:
                target = self.GWIMUNGWAN_SAL[jiji]
                if target in jiji_list:
                    found_pairs.append(f'{jiji}-{target}')
        
        return {
            'found_pairs': list(set(found_pairs)),
            'has_gwimungwan': len(found_pairs) > 0,
            'description': '정신적 이상, 의처증, 의부증, 변태 기질이 생김. 때로는 비상한 두뇌를 뜻하기도 함.'
        }

    def get_sal_analysis(self, sal_results: Dict[str, any]) -> str:
        """살 분석 결과를 텍스트로 생성"""
        if not sal_results:
            return "살 계산에 실패했습니다."
        
        saju = sal_results.get('saju', {})
        
        analysis = f"""
=== 살(煞) 분석 결과 ===

[기본 사주]
연주: {saju.get('year_pillar', '')} (年柱)
월주: {saju.get('month_pillar', '')} (月柱)  
일주: {saju.get('day_pillar', '')} (日柱)
시주: {saju.get('hour_pillar', '')} (時柱)

생년월일: {saju.get('birth_date', '')}
생시: {saju.get('birth_time', '')}

[길성(吉星) 분석]
"""
        
        # 길성들 분석
        gil_seong_list = [
            ('cheonul_gwiin', '천을귀인', '🌟'),
            ('munchang_gwiin', '문창귀인', '📚'),
            ('bokseong_gwiin', '복성귀인', '🍀'),
            ('woldeok_gwiin', '월덕귀인', '🌙'),
            ('cheondeok_gwiin', '천덕귀인', '☀️'),
            ('wolgong_gwiin', '월공귀인', '🌕'),
            ('geumyeo', '금여', '💍'),
            ('geonrok', '건록', '🏛️'),
            ('amrok', '암록', '🎁'),
            ('cheonuiseong', '천의성', '⚕️'),
            ('banan_sal', '반안살', '🏆')
        ]
        
        for key, name, emoji in gil_seong_list:
            result = sal_results.get(key, {})
            has_key = f'has_{key.split("_")[0]}'  # has_cheonul, has_munchang 등
            if result.get(has_key):
                positions = result.get('positions', [])
                analysis += f"{emoji} {name}: {', '.join(positions)}\n"
                analysis += f"   → {result.get('description', '')}\n\n"
        
        # 삼기 분석
        samgi = sal_results.get('samgi', {})
        if samgi.get('has_samgi'):
            analysis += "✨ 삼기:\n"
            for samgi_info in samgi.get('found_samgi', []):
                analysis += f"   → {samgi_info['type']}: {samgi_info['pattern']} ({samgi_info['positions']})\n"
            analysis += f"   → {samgi.get('description')}\n\n"
        
        analysis += "\n[주요 살(煞) 분석]\n"
        
        # 주요 살들
        sal_list = [
            ('dohwa_sal', '도화살', '🌸'),
            ('yeokma_sal', '역마살', '🔄'),
            ('hwagae_sal', '화개살', '🎨')
        ]
        
        for key, name, emoji in sal_list:
            result = sal_results.get(key, {})
            if result.get(f'has_{key.split("_")[0]}'):
                positions = result.get('positions', [])
                analysis += f"{emoji} {name}: {', '.join(positions)}\n"
                analysis += f"   → {result.get('description', '')}\n\n"
        
        # 공망살
        gongmang = sal_results.get('gongmang_sal', {})
        if gongmang.get('has_gongmang'):
            analysis += f"🕳️ 공망살: {', '.join(gongmang.get('gongmang_jiji', []))}\n"
            for pos in gongmang.get('positions', []):
                analysis += f"   → {pos['pillar']}: {pos['jiji']}\n"
            analysis += f"   → {gongmang.get('description')}\n\n"
        
        analysis += "\n[흉살(凶煞) 분석]\n"
        
        # 흉살들
        흉살_list = [
            ('yangin_sal', '양인살', '⚔️'),
            ('baekho_sal', '백호살', '🐅'),
            ('gwaegang_sal', '괴강살', '⚡'),
            ('hongyeom_sal', '홍염살', '💋'),
            ('geupgak_sal', '급각살', '🦵'),
            ('geop_sal', '겁살', '💸'),
            ('mangsin_sal', '망신살', '😳')
        ]
        
        for key, name, emoji in 흉살_list:
            result = sal_results.get(key, {})
            has_key = f'has_{key.split("_")[0]}'
            if result.get(has_key):
                positions = result.get('positions', [])
                if positions:
                    analysis += f"{emoji} {name}: {', '.join(positions)}\n"
                else:
                    analysis += f"{emoji} {name}: 일주\n"
                analysis += f"   → {result.get('description', '')}\n\n"
        
        # 현침살
        hyeonchim = sal_results.get('hyeonchim_sal', {})
        if hyeonchim.get('has_hyeonchim'):
            analysis += "🔍 현침살:\n"
            for char_info in hyeonchim.get('found_chars', []):
                analysis += f"   → {char_info['char']} ({char_info['type']}, {char_info['pillar']})\n"
            analysis += f"   → {hyeonchim.get('description')}\n\n"
        
        # 수옥살
        suok = sal_results.get('suok_sal', {})
        if suok.get('has_suok'):
            analysis += "🔒 수옥살:\n"
            for pos in suok.get('positions', []):
                analysis += f"   → {pos['pillar']}: {pos['jiji']}\n"
            analysis += f"   → {suok.get('description')}\n\n"
        
        # 천라지망살
        cheonra_jimang = sal_results.get('cheonra_jimang', {})
        if cheonra_jimang.get('has_cheonra_jimang'):
            if cheonra_jimang.get('has_cheonra'):
                analysis += "🕸️ 천라살: 戌亥 조합\n"
            if cheonra_jimang.get('has_jimang'):
                analysis += "🕸️ 지망살: 辰巳 조합\n"
            analysis += f"   → {cheonra_jimang.get('description')}\n\n"
        
        # 원진살
        wonjin = sal_results.get('wonjin_sal', {})
        if wonjin.get('has_wonjin'):
            analysis += f"😠 원진살: {', '.join(wonjin.get('found_pairs', []))}\n"
            analysis += f"   → {wonjin.get('description')}\n\n"
        
        # 귀문관살
        gwimungwan = sal_results.get('gwimungwan_sal', {})
        if gwimungwan.get('has_gwimungwan'):
            analysis += f"👻 귀문관살: {', '.join(gwimungwan.get('found_pairs', []))}\n"
            analysis += f"   → {gwimungwan.get('description')}\n\n"
        
        return analysis.strip()
    
    def fortune_analyze(self, birth_date: str, birth_time: str) -> str:
        """
        살 계산 결과를 바탕으로 운세 분석을 생성합니다.
        이 함수는 프롬프트 엔지니어링을 통해 자세한 운세 해석을 제공합니다.
        """
        sal_results = self.calculate_sal(birth_date, birth_time)
        if not sal_results:
            return "운세 분석에 실패했습니다."
        
        # 기본 살 분석
        basic_analysis = self.get_sal_analysis(sal_results)
        
        # 프롬프트 엔지니어링을 통한 상세 운세 분석
        fortune_prompt = self._generate_fortune_prompt(sal_results)
        
        # 종합 운세 분석 결과
        comprehensive_analysis = f"""
{basic_analysis}

=== 종합 운세 분석 ===
{fortune_prompt}
        """
        
        return comprehensive_analysis.strip()
    
    def _generate_fortune_prompt(self, sal_results: Dict[str, any]) -> str:
        """프롬프트 엔지니어링을 통한 운세 분석 생성"""
        fortune_elements = []
        
        # 길성 영향 분석
        if sal_results.get('cheonul_gwiin', {}).get('has_cheonul'):
            fortune_elements.append("천을귀인의 가호로 인생에서 귀인의 도움을 받아 큰 성공을 이룰 수 있습니다.")
        
        if sal_results.get('munchang_gwiin', {}).get('has_munchang'):
            fortune_elements.append("문창귀인의 영향으로 학업과 시험에서 좋은 성과를 거둘 것입니다.")
        
        if sal_results.get('bokseong_gwiin', {}).get('has_bokseong'):
            fortune_elements.append("복성귀인으로 인해 평생 의식주 걱정 없이 살 수 있을 것입니다.")
        
        if sal_results.get('woldeok_gwiin', {}).get('has_woldeok'):
            fortune_elements.append("월덕귀인의 덕택으로 명예와 품성이 인정받아 공직이나 관직에 오를 수 있습니다.")
        
        if sal_results.get('cheondeok_gwiin', {}).get('has_cheondeok'):
            fortune_elements.append("천덕귀인의 보호로 각종 재난과 위험에서 안전하게 지켜질 것입니다.")
        
        if sal_results.get('geumyeo', {}).get('has_geumyeo'):
            fortune_elements.append("금여의 영향으로 배우자운이 좋아 좋은 인연을 만날 수 있습니다.")
        
        if sal_results.get('geonrok', {}).get('has_geonrok'):
            fortune_elements.append("건록의 기운으로 건강하고 의지가 강하며 안정적인 직장 생활을 할 수 있습니다.")
        
        # 주요 살 영향 분석
        if sal_results.get('dohwa_sal', {}).get('has_dohwa'):
            fortune_elements.append("도화살이 있어 이성운이 좋지만 유혹에 빠지지 않도록 주의해야 합니다.")
        
        if sal_results.get('yeokma_sal', {}).get('has_yeokma'):
            fortune_elements.append("역마살의 영향으로 이동과 변화가 많은 삶을 살게 되며, 해외 활동이나 여행에 유리합니다.")
        
        if sal_results.get('hwagae_sal', {}).get('has_hwagae'):
            fortune_elements.append("화개살이 있어 예술적 재능이 뛰어나지만 인복에 따라 길흉이 달라질 수 있습니다.")
        
        # 흉살 영향 분석
        if sal_results.get('yangin_sal', {}).get('has_yangin'):
            fortune_elements.append("양인살이 있어 강한 기운을 가지고 있지만 사고나 부상을 조심해야 합니다.")
        
        if sal_results.get('baekho_sal', {}).get('has_baekho'):
            fortune_elements.append("백호살이 있어 교통사고나 질병을 특히 조심하고 안전에 각별히 주의해야 합니다.")
        
        if sal_results.get('gwaegang_sal', {}).get('has_gwaegang'):
            fortune_elements.append("괴강살이 있어 극도로 총명하지만 극단적인 성향이 있어 균형을 유지하는 것이 중요합니다.")
        
        if sal_results.get('gongmang_sal', {}).get('has_gongmang'):
            positions = sal_results.get('gongmang_sal', {}).get('positions', [])
            for pos in positions:
                if pos['pillar'] == '연주':
                    fortune_elements.append("연주에 공망이 있어 부모와의 인연이 약할 수 있습니다.")
                elif pos['pillar'] == '월주':
                    fortune_elements.append("월주에 공망이 있어 형제나 동료와의 관계에서 허무함을 느낄 수 있습니다.")
                elif pos['pillar'] == '일주':
                    fortune_elements.append("일주에 공망이 있어 배우자와의 관계에 공허함이 있을 수 있습니다.")
                elif pos['pillar'] == '시주':
                    fortune_elements.append("시주에 공망이 있어 자녀와의 인연이나 말년운에 주의가 필요합니다.")
        
        # 종합 운세 메시지
        if not fortune_elements:
            fortune_elements.append("특별한 살이 발견되지 않아 평범하고 안정적인 삶을 살 것으로 보입니다.")
        
        fortune_text = "\n".join([f"• {element}" for element in fortune_elements])
        
        # 조언 추가
        advice = self._generate_advice(sal_results)
        
        return f"{fortune_text}\n\n[인생 조언]\n{advice}"
    
    def _generate_advice(self, sal_results: Dict[str, any]) -> str:
        """살 분석 결과를 바탕으로 조언 생성"""
        advice_list = []
        
        # 길성 기반 조언
        if sal_results.get('cheonul_gwiin', {}).get('has_cheonul'):
            advice_list.append("귀인의 도움을 적극적으로 받아들이고 감사하는 마음을 가지세요.")
        
        if sal_results.get('munchang_gwiin', {}).get('has_munchang'):
            advice_list.append("학습과 자기계발에 꾸준히 투자하면 큰 성과를 얻을 수 있습니다.")
        
        # 살 기반 조언
        if sal_results.get('dohwa_sal', {}).get('has_dohwa'):
            advice_list.append("이성 관계에서는 신중함을 잃지 말고 진정한 사랑을 찾으세요.")
        
        if sal_results.get('yeokma_sal', {}).get('has_yeokma'):
            advice_list.append("변화를 두려워하지 말고 새로운 기회에 적극적으로 도전하세요.")
        
        if sal_results.get('yangin_sal', {}).get('has_yangin'):
            advice_list.append("강한 에너지를 건설적인 방향으로 활용하고 안전에 항상 주의하세요.")
        
        if sal_results.get('baekho_sal', {}).get('has_baekho'):
            advice_list.append("위험한 상황을 피하고 건강 관리에 각별히 신경 쓰세요.")
        
        if sal_results.get('gongmang_sal', {}).get('has_gongmang'):
            advice_list.append("때로는 혼자만의 시간을 갖고 내면의 평화를 찾으세요.")
        
        if not advice_list:
            advice_list.append("균형 잡힌 삶을 위해 꾸준한 노력과 인내심을 기르시기 바랍니다.")
        
        return "\n".join([f"• {advice}" for advice in advice_list])


# 사용 예시
if __name__ == "__main__":
    sal_calculator = SalCalculator()
    
    # 테스트
    test_date = "1990-05-15"
    test_time = "14:30"
    
    print("=== 살(煞) 계산기 테스트 ===")
    sal_results = sal_calculator.calculate_sal(test_date, test_time)
    
    if sal_results:
        analysis = sal_calculator.get_sal_analysis(sal_results)
        print(analysis)
        
        print("\n" + "="*50)
        print("=== 종합 운세 분석 ===")
        fortune = sal_calculator.fortune_analyze(test_date, test_time)
        print(fortune)
    else:
        print("살 계산에 실패했습니다.")
