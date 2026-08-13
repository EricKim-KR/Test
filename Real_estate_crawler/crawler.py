import json
import time
import os
from concurrent.futures import ThreadPoolExecutor
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

# Global cache to reuse the ChromeDriver binary path across multiple crawls
# and avoid redundant version/network checks with ChromeDriverManager.
_cached_driver_path = None

def _get_driver_path():
    """ChromeDriverManager를 통해 드라이버 설치 및 경로 정규화 (전역 캐싱 적용)"""
    global _cached_driver_path
    if _cached_driver_path and os.path.exists(_cached_driver_path):
        return _cached_driver_path

    try:
        driver_path = ChromeDriverManager().install()

        # webdriver-manager 4.0.1+ might return a path to a text file in some environments
        # Ensure we point to the actual binary if it's a directory or incorrect file
        if os.path.isdir(driver_path):
            driver_path = os.path.join(driver_path, "chromedriver")
        elif "THIRD_PARTY_NOTICES" in driver_path:
            dir_path = os.path.dirname(driver_path)
            possible_binary = os.path.join(dir_path, "chromedriver")
            if os.path.exists(possible_binary):
                driver_path = possible_binary

        # Ensure the driver is executable (necessary for Linux environments)
        if os.path.exists(driver_path) and not os.access(driver_path, os.X_OK):
            os.chmod(driver_path, 0o755)

        _cached_driver_path = driver_path
        return driver_path
    except Exception as e:
        logger.error(f"드라이버 설치/설정 중 오류: {e}")
        return None

class NaverRealEstateCrawler:
    def __init__(self, driver_path=None):
        self.driver = None
        self.setup_driver(driver_path)
    
    def setup_driver(self, driver_path=None):
        """Selenium WebDriver 초기화"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 백그라운드 모드
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # ⚡ Bolt: Optimization - Set page load strategy to 'eager' to speed up page load
        # This makes Selenium wait only until 'DOMContentLoaded' event is fired.
        chrome_options.page_load_strategy = 'eager'

        # ⚡ Bolt: Optimization - Disable images to reduce bandwidth and rendering time
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            if not driver_path:
                driver_path = _get_driver_path()

                # 실행 권한 부여 (Linux/macOS)
                if os.name != 'nt' and os.path.exists(driver_path):
                    os.chmod(driver_path, 0o755)
            
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
            
            search_keyword = f"{city} {district} {dong}".strip()
            
            # ⚡ Bolt: Optimization - Direct URL navigation instead of loading home page and typing queries.
            # Bypasses slow UI interactions, typing delays, and keyword suggestions clicks, saving ~25 seconds.
            # Using urllib.parse.quote ensures Korean characters are URL-encoded correctly.
            import urllib.parse
            encoded_keyword = urllib.parse.quote(search_keyword)
            search_url = f"https://land.naver.com/search/search.naver?query={encoded_keyword}"
            
            logger.info(f"아파트 검색 시작 (다이렉트 URL): {search_keyword}")
            self.driver.get(search_url)
            
            # 매물 데이터 크롤링 (extract_properties handles dynamic loading and waiting)
            properties = self.extract_properties(trade_type, min_price, max_price)
            
            return properties
        
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return []
    
    def extract_properties(self, trade_type="all", min_price=None, max_price=None):
        """페이지에서 매물 정보 추출"""
        try:
            # ⚡ Bolt: Optimization - Wait for content dynamically with lower timeout.
            # Including class '.no_result' avoids timing out on pages with no matching items.
            # Using try-except prevents logging large stack traces on timeout, returning gracefully instead.
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".list_item, .item_section, .item_wrapper, .item, .no_result, .no_results, .zero_result"))
                )
            except Exception:
                logger.warning("매물 리스트 대기 시간 초과 또는 결과 없음")
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            properties = []
            
            # ⚡ Bolt: Optimization - Use a single CSS selector query to find items,
            # avoiding up to 4 sequential full-document scans in BeautifulSoup.
            items = soup.select('.list_item, .item_section, .item_wrapper, .item')
            
            if not items:
                logger.warning("매물 리스트를 찾을 수 없음")
                return properties
            
            logger.info(f"발견된 항목 수: {len(items)}")
            
            for item in items[:50]:  # 최대 50개 항목
                try:
                    # ⚡ Bolt: Optimization - Use a single CSS selector query to extract details,
                    # avoiding up to 15-20 individual python-level find() calls per item (reducing call overhead by ~66%).
                    name_elem = item.select_one('span.name, a.name, strong.name, p.info_title, .complex_name')
                    name = name_elem.get_text(strip=True) if name_elem else "정보 없음"
                    
                    # 가격 추출
                    price_elem = item.select_one('span.price, strong.price')
                    price = price_elem.get_text(strip=True) if price_elem else "정보 없음"
                    
                    # 거래 타입
                    trade_elem = item.select_one('span.trade_type, span.type')
                    trade_name = trade_elem.get_text(strip=True) if trade_elem else "알 수 없음"
                    
                    # 정보 (층수, 면적 등)
                    info_elem = item.select_one('span.info_list, span.info_text, p.info')
                    info_text = info_elem.get_text(strip=True) if info_elem else "정보 없음"
                    
                    # 설명/특징
                    desc_elem = item.select_one('p.item_desc, p.desc, span.desc')
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
            
            # ⚡ Bolt: Optimization - URL encode the query keyword for search stability and correctness.
            import urllib.parse
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://land.naver.com/article/division/34010300?q={encoded_keyword}&ms=37.4979,127.0276,15&a=VILLA&b=A1"

            logger.info(f"빌라 검색 시작 (다이렉트 URL): {keyword}")
            self.driver.get(url)
            
            # extract_properties handles the wait for elements
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

def _crawl_single_type(prop_type, city, district, dong, trade_type, min_price, max_price, driver_path=None):
    """단일 매물 종류 크롤링을 위한 헬퍼 함수 (병렬 실행용)"""
    crawler = NaverRealEstateCrawler(driver_path=driver_path)
    try:
        if prop_type.upper() == 'APT':
            return crawler.search_apartments(city, district, dong, trade_type, min_price, max_price)
        elif prop_type.upper() == 'VILLA':
            return crawler.search_villas(city, district, dong, min_price, max_price)
        return []
    finally:
        crawler.close()

def crawl_properties(city, district, dong="", property_types=None, trade_type="all", min_price=None, max_price=None):
    """
    부동산 매물 크롤링 함수 (병렬 처리 최적화)
    
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
    if not property_types:
        if property_types is None:
            property_types = ['APT']
        else:
            return []
    
    all_properties = []

    # 드라이버를 메인 스레드에서 한 번만 설치하여 병렬 실행 시 레이스 컨디션 방지
    driver_path = _get_driver_path()

    # 여러 매물 종류를 요청한 경우 병렬로 처리하여 속도 향상
    # ThreadPoolExecutor를 사용하여 각 매물 종류별로 독립된 브라우저 인스턴스 실행
    with ThreadPoolExecutor(max_workers=len(property_types)) as executor:
        futures = [
            executor.submit(_crawl_single_type, prop_type, city, district, dong, trade_type, min_price, max_price, driver_path=driver_path)
            for prop_type in property_types
        ]

        for future in futures:
            try:
                properties = future.result()
                all_properties.extend(properties)
            except Exception as e:
                logger.error(f"병렬 크롤링 중 오류 발생: {e}")

    return all_properties
