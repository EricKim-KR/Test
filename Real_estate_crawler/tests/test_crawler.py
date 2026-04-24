import pytest
from unittest.mock import MagicMock, patch
from crawler import NaverRealEstateCrawler, crawl_properties

@pytest.fixture
def mock_driver():
    with patch('crawler.webdriver.Chrome') as mock_chrome:
        mock_instance = MagicMock()
        mock_chrome.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def crawler(mock_driver):
    with patch('crawler.ChromeDriverManager'):
        crawler = NaverRealEstateCrawler()
        return crawler

def test_extract_properties(crawler):
    """Test extract_properties method with mock HTML."""
    mock_html = """
    <div class="list_item">
        <span class="name">테스트 아파트</span>
        <span class="price">10억</span>
        <span class="trade_type">매매</span>
        <span class="info_list">84/110㎡</span>
        <p class="item_desc">설명</p>
    </div>
    """
    crawler.driver.page_source = mock_html

    properties = crawler.extract_properties(trade_type="all")

    assert len(properties) == 1
    assert properties[0]['name'] == "테스트 아파트"
    assert properties[0]['price'] == "10억"
    assert properties[0]['trade_type'] == "매매"

def test_extract_properties_filtering(crawler):
    """Test extract_properties with trade_type filtering."""
    mock_html = """
    <div class="list_item">
        <span class="name">매매 매물</span>
        <span class="trade_type">매매</span>
    </div>
    <div class="list_item">
        <span class="name">전세 매물</span>
        <span class="trade_type">전세</span>
    </div>
    """
    crawler.driver.page_source = mock_html

    # Test sale (매매) filter
    properties = crawler.extract_properties(trade_type="sale")
    assert len(properties) == 1
    assert properties[0]['name'] == "매매 매물"

    # Test jeonse (전세) filter
    properties = crawler.extract_properties(trade_type="jeonse")
    assert len(properties) == 1
    assert properties[0]['name'] == "전세 매물"

@patch('crawler.NaverRealEstateCrawler.setup_driver')
@patch('crawler.NaverRealEstateCrawler.search_apartments')
@patch('crawler.NaverRealEstateCrawler.close')
def test_crawl_properties_function(mock_close, mock_search, mock_setup):
    """Test the crawl_properties wrapper function."""
    mock_search.return_value = [{"name": "APT 1"}]

    results = crawl_properties("서울", "강남구", property_types=['APT'])

    assert len(results) == 1
    assert results[0]['name'] == "APT 1"
    mock_search.assert_called_once()
    mock_close.assert_called_once()
