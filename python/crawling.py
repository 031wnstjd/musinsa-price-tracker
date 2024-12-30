from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import pymongo
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 로그 포맷 설정
    handlers=[
        logging.FileHandler("app.log"),  # 로그를 파일에 저장
        logging.StreamHandler()  # 콘솔에 출력
    ]
)

# selector 정의
item_selector = ".sc-fUnNpA";
brand_selector = '.text-etc_11px_semibold'
name_selector = '.text-body_13px_reg'
price_selector = '.text-body_13px_semi:not(.text-red)'
discount_rate_selector = '.text-red'

def crawl_products(url): 
    # MongoDB 설정
    client = connect_to_mongo_db("mongodb://admin:admin@127.0.0.1:27017/?authSource=admin")
    db = client["musinsa"] # 사용할 데이터베이스 이름
    collection = db["products"] # 사용할 컬렉션 이름
    
    '''
    # TODO: headless 옵션 설정 시 크롤링 데이터 개수 달라지는 문제 해결 필요 
    Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없는 환경에서 사용
    chrome_options.add_argument('--window-size=430,932') # 창 크기 명시 (모바일 웹 사이즈)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # 메모리 문제 방지
    
    # ChromeDriver 설정 및 실행
    # service = Service(ChromeDriverManager().install())  # ChromeDriver 자동 설치 및 경로 설정
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    '''
    
    driver = webdriver.Chrome()
    
    try:
        driver.get(url)
        
        time.sleep(5) # 초기 로딩을 위한 대기 시간간
        
        total_product_cnt = 0 # 상품 총개수 초기값 설정
        
        while True:
            # 현재 페이지에서 상품 정보 크롤링
            products = driver.find_elements(By.CSS_SELECTOR, item_selector)
            
            logging.info(f"상품 개수: {len(products)}")
        
            brands = []
            
            for product in products:
                try:
                    brand = product.find_element(By.CSS_SELECTOR, brand_selector).text
                    name = product.find_element(By.CSS_SELECTOR, name_selector).text
                    price = parse_price_to_integer(product.find_element(By.CSS_SELECTOR, price_selector).text)
                    try:
                        discount_rate = parse_discount_rate_to_float(product.find_element(By.CSS_SELECTOR, discount_rate_selector).text)
                    except:
                        discount_rate = 0.0 # 할인 정보가 없을 때
                        # logging.info("할인 정보가 없습니다.")
                        
                    product_id = generate_hash_id(brand, name)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 예시: '2024-12-26 15:30:00'
                    
                    # MongoDB에 저장할 데이터 준비
                    product_data = {
                        "product_id": product_id,
                        "brand": brand,
                        "name": name,
                        "price": price,
                        "discount_rate": discount_rate,
                        "timestamp": timestamp
                    }
                    
                    collection.insert_one(product_data)
                    
                    brands.append(brand)
                    
                    # logging.info(f"상품ID: {product_id}")
                    # logging.info(f"브랜드: {brand}")
                    # logging.info(f"상품명: {name}")
                    # logging.info(f"가격: {price}")
                    # logging.info(f"할인율: {discount_rate}")
                    # logging.info(f"현재시각: {timestamp}")
                    # logging.info("===================================")
                    
                    total_product_cnt += 1
                except Exception as e:
                    logging.error(f"상품 데이터를 가져오지 못했습니다. {product_data}, {e}")
                    continue # 일부 상품에서 데이터를 가져오지 못해도 진행        
            
            logging.info(brands)
            
            if not scroll_to_end(driver, scroll_pouse_time=60):
                logging.info("더 이상 스크롤할 내용이 없습니다.")
                break
    
        # 크롤링 결과 출력
        print(f"총 {total_product_cnt} 개의 상품을 수집했습니다.")
        
    except Exception as e:
        logging.error("에러 발생: %s", e)  
    finally:
        # 브라우저 종료
        driver.quit()

def connect_to_mongo_db(url):
    try:
        client = pymongo.MongoClient(url)
        logging.info("MongoDB 연결 성공")
    except pymongo.errors.ConnectionFailure as e:
        logging.error("MongoDB 연결 실패: %s", e) 
    return client

def scroll_to_end(driver, scroll_pouse_time = 60):
    # 현재 페이지 높이
    cur_height = driver.execute_script("return document.body.scrollHeight")
    logging.info(cur_height)
    
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    
    try:
        # 새 콘텐츠 로드될 때까지 대기
        WebDriverWait(driver, scroll_pouse_time).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, item_selector))
        )
        return True
    
        # TODO: 페이지 높이 변화 없으면 False 리턴하도록 로직 추가하기
    except TimeoutException:
        return False
        
def generate_hash_id(brand, name):
    # 브랜드명과 상품명을 합침
    combined_str = f"{brand}{name}"
    
    # SHA-256 해시 알고리즘을 사용하여 해시 생성
    hash_object = hashlib.sha256(combined_str.encode())
    
    # 해시 값을 16진수 문자열로 반환
    hash_id = hash_object.hexdigest()
    
    return hash_id

def parse_price_to_integer(price):
    return int(price.replace(",", "").replace("원", ""))

def parse_discount_rate_to_float(discount_rate):
    return float(discount_rate.replace("%", "")) / 100