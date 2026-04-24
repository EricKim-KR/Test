import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaverRealEstateCrawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Selenium WebDriver 초기화"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 백그라운드 모드
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            import os
            driver_path = ChromeDriverManager().install()
            if not driver_path.endswith(".exe"):
                dir_path = os.path.dirname(driver_path)
                driver_path = os.path.join(dir_path, "chromedriver.exe")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info(f"WebDriver 초기화 성공: {driver_path}")
        except Exception as e:
            logger.error(f"WebDriver 초기화 실패: {e}")
            raise
    
    def search_apartments(self, city, district, dong="", trade_type="all", min_price=None, max_price=None):
        """
        네이버 부동산에서 아파트 검색
        
        Args:
            city: 시 (예: 서울시)
            district: 구 (예: 강남구)
            dong: 동 (예: 개포동, 선택사항)
            trade_type: 거래 유형 - 'all', 'sale', 'jeonse', 'monthly'
            min_price: 최소 가격 (억)
            max_price: 최대 가격 (억)
        
        Returns:
            매물 정보 리스트
        """
        try:
            # 지역 정보 정규화
            city = city.replace('시', '').strip()
            district = district.replace('구', '').strip()
            
            # 네이버 부동산 검색 URL 구성
            search_url = f"https://land.naver.com/article/division/34010000?ms=37.4979,127.0276,15&a=APT&b=A1&c=&d=&e=&f=&g=&h=&i=&j=&k=&l=&m=&n=&o=&p=&q=&r=&s=&t=&aa=&bb=&cc=&dd=&ee=&ff=&showR=Y&scortOrder=dddsc&one=1&page=1"
            
            logger.info(f"검색 시작: {city} {district} {dong}")
            self.driver.get("https://land.naver.com/")
            time.sleep(2)
            
            # 검색어 입력
            try:
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "input_search"))
                )
                search_keyword = f"{city} {district} {dong}".strip()
                search_input.clear()
                search_input.send_keys(search_keyword)
                time.sleep(1)
                
                # 첫 번째 검색 결과 클릭
                try:
                    suggestion = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "keyword_list_item"))
                    )
                    suggestion.click()
                except:
                    logger.warning("검색 결과 자동완성 없음, 엔터로 직접 검색")
                    search_input.submit()
                
                time.sleep(3)
            except Exception as e:
                logger.error(f"검색 입력 실패: {e}")
            
            # 매물 데이터 크롤링
            properties = self.extract_properties(trade_type, min_price, max_price)
            
            return properties
        
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return []
    
    def extract_properties(self, trade_type="all", min_price=None, max_price=None):
        """페이지에서 매물 정보 추출"""
        try:
            # 페이지 로딩 대기
            time.sleep(2)
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            properties = []
            
            # 매물 리스트 항목 추출 (다양한 선택자 시도)
            items = soup.find_all('div', class_='list_item')
            if not items:
                items = soup.find_all('article', class_='item_section')
            if not items:
                items = soup.find_all('div', class_='item_wrapper')
            if not items:
                items = soup.find_all('li', class_='item')
            
            if not items:
                logger.warning("매물 리스트를 찾을 수 없음")
                return properties
            
            logger.info(f"발견된 항목 수: {len(items)}")
            
            for item in items[:50]:  # 최대 50개 항목
                try:
                    # 매물명 - 다양한 셀렉터 시도
                    name_elem = item.find('span', class_='name') or \
                               item.find('a', class_='name') or \
                               item.find('strong', class_='name') or \
                               item.find('p', class_='info_title') or \
                               item.find(class_='complex_name')
                    name = name_elem.get_text(strip=True) if name_elem else "정보 없음"
                    
                    # 가격 추출
                    price_elem = item.find('span', class_='price') or \
                                item.find('strong', class_='price')
                    price = price_elem.get_text(strip=True) if price_elem else "정보 없음"
                    
                    # 거래 타입
                    trade_elem = item.find('span', class_='trade_type') or \
                                item.find('span', class_='type')
                    trade_name = trade_elem.get_text(strip=True) if trade_elem else "알 수 없음"
                    
                    # 정보 (층수, 면적 등)
                    info_elem = item.find('span', class_='info_list') or \
                               item.find('span', class_='info_text') or \
                               item.find('p', class_='info')
                    info_text = info_elem.get_text(strip=True) if info_elem else "정보 없음"
                    
                    # 설명/특징
                    desc_elem = item.find('p', class_='item_desc') or \
                               item.find('p', class_='desc') or \
                               item.find('span', class_='desc')
                    desc = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # 필터링
                    if trade_type != "all":
                        if trade_type == "sale" and "매매" not in trade_name:
                            continue
                        elif trade_type == "jeonse" and "전세" not in trade_name:
                            continue
                        elif trade_type == "monthly" and "월세" not in trade_name:
                            continue
                    
                    property_data = {
                        "name": name,
                        "price": price,
                        "trade_type": trade_name,
                        "info": info_text,
                        "description": desc,
                        "type": "아파트"
                    }
                    
                    properties.append(property_data)
                    logger.info(f"매물 추출: {name} - {price}")
                    
                except Exception as e:
                    logger.warning(f"항목 파싱 오류: {e}")
                    continue
            
            logger.info(f"총 {len(properties)}개 매물 추출 완료")
            return properties
        
        except Exception as e:
            logger.error(f"데이터 추출 중 오류: {e}")
            return []
    
    def search_villas(self, city, district, dong="", min_price=None, max_price=None):
        """빌라/연립주택 검색"""
        try:
            keyword = f"{city} {district} {dong}".strip()
            url = f"https://land.naver.com/article/division/34010300?q={keyword}&ms=37.4979,127.0276,15&a=VILLA&b=A1"
            
            logger.info(f"빌라 검색 시작: {keyword}")
            self.driver.get(url)
            time.sleep(3)
            
            properties = self.extract_properties("all", min_price, max_price)
            return properties
        
        except Exception as e:
            logger.error(f"빌라 검색 중 오류: {e}")
            return []
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver 종료")

def crawl_properties(city, district, dong="", property_types=None, trade_type="all", min_price=None, max_price=None):
    """
    부동산 매물 크롤링 함수
    
    Args:
        city: 시
        district: 구
        dong: 동 (선택)
        property_types: 매물 종류 (기본값: ['APT'])
        trade_type: 거래 유형 ('all', 'sale', 'jeonse', 'monthly')
        min_price: 최소 가격 (억)
        max_price: 최대 가격 (억)
    
    Returns:
        매물 정보 리스트
    """
    if property_types is None:
        property_types = ['APT']
    
    crawler = NaverRealEstateCrawler()
    all_properties = []
    
    try:
        for prop_type in property_types:
            if prop_type.upper() == 'APT':
                properties = crawler.search_apartments(city, district, dong, trade_type, min_price, max_price)
            elif prop_type.upper() == 'VILLA':
                properties = crawler.search_villas(city, district, dong, min_price, max_price)
            else:
                continue
            
            all_properties.extend(properties)
        
        return all_properties
    
    finally:
        crawler.close()
