# 🚀 빠른 시작 가이드

## 1단계: 의존성 설치

PowerShell에서 다음 명령 실행:

```powershell
cd d:\GitHub\Test\Real_estate_crawler
pip install -r requirements.txt
```

## 2단계: 애플리케이션 실행

```powershell
python app.py
```

정상 실행되면 다음과 같은 메시지가 나타납니다:
```
 * Running on http://127.0.0.1:5000
```

## 3단계: 웹 브라우저에서 접속

브라우저 주소창에 입력:
```
http://localhost:5000
```

## 4단계: 부동산 검색

1. **지역 입력**
   - 시: `서울` (또는 다른 도시)
   - 구: `강남구` (또는 다른 구)
   - 동: `개포동` (선택사항)

2. **매물 종류**: 아파트 또는 빌라/연립 선택

3. **거래 유형**: 전체, 매매, 전세, 월세 선택

4. **"네이버 검색 실행" 버튼 클릭**

## 📌 주의사항

⏱️ **첫 검색은 2-3분 소요됩니다**

- Selenium이 네이버 부동산 페이지를 동적으로 로드합니다
- Chrome 브라우저 창이 자동으로 열립니다 (headless 모드 사용 시 열리지 않음)

## 🆘 문제 해결

### 1. "WebDriver 초기화 실패" 오류

**해결방법**:
```powershell
pip install --upgrade webdriver-manager
```

### 2. Chrome이 설치되지 않았습니다

**해결방법**:
- Chrome 브라우저 설치: https://www.google.com/chrome
- 또는 Edge, Chromium 등 Chromium 기반 브라우저 사용 가능

### 3. 의존성 설치 오류

**해결방법**:
```powershell
# 기존 환경 삭제
pip uninstall -r requirements.txt -y

# 재설치
pip install -r requirements.txt
```

## 📊 검색 결과 활용

- **CSV 다운로드**: "Excel 추출" 버튼으로 결과 저장
- **재검색**: 조건 변경 후 "네이버 검색 실행" 버튼 다시 클릭

## 💡 팁

- 처음엔 도/시 + 구 정도의 큰 단위로 검색하기
- 원하는 결과가 없으면 동명까지 입력해서 세밀하게 검색
- 가격 범위를 설정하면 더 정확한 결과 조회 가능

## 📚 더 자세한 내용

[README.md](README.md) 파일 참조
