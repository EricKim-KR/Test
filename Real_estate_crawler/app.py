from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from crawler import crawl_properties
import logging
import json
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_properties():
    """
    부동산 매물 검색 API
    
    요청 데이터:
    {
        "city": "서울시",
        "district": "강남구",
        "dong": "개포동",
        "property_types": ["APT", "VILLA"],
        "trade_type": "all",
        "min_price": 10,
        "max_price": 50
    }
    """
    try:
        data = request.get_json()
        
        city = data.get('city', '').strip()
        district = data.get('district', '').strip()
        dong = data.get('dong', '').strip()
        property_types = data.get('propertyTypes', ['APT'])
        trade_type = data.get('tradeType', 'all')
        min_price = data.get('minPrice')
        max_price = data.get('maxPrice')
        
        # 입력값 검증
        if not city or not district:
            return jsonify({'error': '시와 구 정보는 필수입니다'}), 400
        
        # 가격 변환
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
        
        logger.info(f"검색 요청: {city} {district} {dong}, Types: {property_types}, Trade: {trade_type}")
        
        # 크롤링 실행
        properties = crawl_properties(
            city=city,
            district=district,
            dong=dong,
            property_types=property_types,
            trade_type=trade_type,
            min_price=min_price,
            max_price=max_price
        )
        
        return jsonify({
            'success': True,
            'count': len(properties),
            'data': properties,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"검색 중 오류: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
