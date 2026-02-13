# 네이버 부동산 실시간 크롤러

네이버 부동산에서 실시간으로 매물 정보를 크롤링하고 분석하는 웹 애플리케이션입니다.

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
cd d:\GitHub\Test\Real_estate_crawler
pip install -r requirements.txt
```

### 2. ChromeDriver 설치

Selenium을 사용하기 위해 ChromeDriver가 필요합니다.

#### Windows에서:
```bash
# 방법 1: WebDriver Manager 사용 (권장)
pip install webdriver-manager
```

#### 또는 수동으로:
1. https://chromedriver.chromium.org/ 에서 현재 Chrome 버전에 맞는 ChromeDriver 다운로드
2. `Real_estate_crawler` 폴더에 `chromedriver.exe` 저장

### 3. 애플리케이션 실행

```bash
python app.py
```

그 후 브라우저에서 `http://localhost:5000` 접속

## 📋 사용 방법

### 웹 인터페이스

1. **지역 입력**: 시, 구, 동을 입력합니다
   - 예: 서울 / 강남구 / 개포동
   
2. **매물 종류 선택**:
   - 아파트
   - 빌라/연립

3. **거래 유형 선택**:
   - 전체보기 (모든 거래 유형)
   - 매매
   - 전세
   - 월세

4. **가격 범위 설정** (선택사항, 억 단위):
   - 최소 가격
   - 최대 가격

5. **"네이버 검색 실행" 버튼 클릭**

### API 사용

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "city": "서울",
    "district": "강남구",
    "dong": "개포동",
    "propertyTypes": ["APT"],
    "tradeType": "all",
    "minPrice": 10,
    "maxPrice": 50
  }'
```

## 📊 응답 형식

```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "name": "개포자이",
      "price": "28억 5,000",
      "trade_type": "매매",
      "info": "12/22층 · 134/168㎡",
      "description": "올수리된 깨끗한 매물",
      "type": "아파트"
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

## ⚙️ 크롤링 특징

- **Selenium 기반**: 동적 콘텐츠 처리 가능
- **BeautifulSoup 파싱**: 안정적인 HTML 파싱
- **다중 거래 유형 지원**: 매매, 전세, 월세 분류
- **가격 필터링**: 관심 가격대의 매물만 조회
- **Excel 내보내기**: 검색 결과를 CSV로 다운로드

## 📝 폴더 구조

```
Real_estate_crawler/
├── app.py              # Flask 애플리케이션 메인 파일
├── crawler.py          # 네이버 부동산 크롤러 로직
├── requirements.txt    # Python 의존성
├── templates/
│   └── index.html      # 웹 인터페이스
└── static/            # 정적 파일 (CSS, JS 등)
```

## 🛠️ 주요 함수

### crawler.py

#### `crawl_properties(city, district, dong="", property_types=None, trade_type="all", min_price=None, max_price=None)`
- 부동산 매물 크롤링
- **매개변수**:
  - `city`: 시 이름 (예: "서울")
  - `district`: 구 이름 (예: "강남구")
  - `dong`: 동 이름 (선택)
  - `property_types`: 매물 종류 리스트 (기본값: ['APT'])
  - `trade_type`: 거래 유형 ('all', 'sale', 'jeonse', 'monthly')
  - `min_price`: 최소 가격 (억 단위)
  - `max_price`: 최대 가격 (억 단위)

#### `NaverRealEstateCrawler` 클래스
- Selenium WebDriver 관리
- 네이버 부동산 검색 및 데이터 추출
- 자동 종료 처리

## ⚠️ 주의사항

1. **첫 실행**: 초기 크롤링은 2-3분 소요될 수 있습니다
2. **Chrome 브라우저**: 설치되어 있어야 합니다
3. **네트워크**: 안정적인 네트워크 연결 필요
4. **약관 준수**: 네이버 약관을 준수하여 적절한 간격으로 크롤링하세요

## 🔧 트러블슈팅

### ChromeDriver 오류
```
WebDriver 초기화 실패
```
**해결방법**:
- ChromeDriver 버전과 Chrome 브라우저 버전 확인
- `webdriver-manager` 설치: `pip install webdriver-manager`
- `crawler.py`에서 자동 다운로드 기능 활성화

### 검색 결과 없음
- 정확한 구/동 이름 확인
- 네이버 부동산에서 직접 검색하여 지역명 확인
- 가격 범위 재검토

## 📄 라이선스

MIT License

## 📧 문의사항

문제가 발생하면, 로그 메시지를 확인하고 필요시 이슈를 등록해주세요.
