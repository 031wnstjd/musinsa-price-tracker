import crawling
import time

# URL 목록 관리
category_urls = {
    "beauty": "https://www.musinsa.com/category/104?gf=A",
    "shoes": "https://www.musinsa.com/category/103?gf=A",
    "outer": "https://www.musinsa.com/category/002?gf=A",
    "top": "https://www.musinsa.com/category/001?gf=A",
    "pants": "https://www.musinsa.com/category/003?gf=A",
    "onepiece_skirt": "https://www.musinsa.com/category/100?gf=A",
    "bag": "https://www.musinsa.com/category/004?gf=A",
    "accessory": "https://www.musinsa.com/category/101?gf=A",
    "underwear": "https://www.musinsa.com/category/026?gf=A",
    "sports_leisure": "https://www.musinsa.com/category/017?gf=A",
    "digital_life": "https://www.musinsa.com/category/102?gf=A",
    "outlet": "https://www.musinsa.com/category/107?gf=A",
    "butique": "https://www.musinsa.com/category/105?gf=A",
    "kids": "https://www.musinsa.com/category/106?gf=A",
    "us": "https://www.musinsa.com/category/108?gf=A",
}

# 크롤링할 카테고리 선택 (필요에 따라 조정 가능)
categories_to_crawl = ["top"]

# 크롤링 실행
def crawl_selected_categories(categories, urls):
    for category in categories:
        if category in urls:
            print(f"크롤링 중: {category} ({urls[category]})")
            crawling.crawl_products(urls[category])
        else:
            print(f"잘못된 카테고리: {category}")

# 크롤링 실행 호출

start_time = time.time()
crawl_selected_categories(categories_to_crawl, category_urls)
end_time = time.time()

execution_time = end_time - start_time
print(f"크롤러 실행 시간: {execution_time:.2f} seconds")