# 데이터 기반 레시피 추천 시스템 (Data-Driven Recipe Recommendation System)

## 소개
이 프로젝트는 사용자가 입력한 재료를 기반으로 최적의 레시피를 추천하고 주재료에 대한 대체할 수 있는 대체재료를 추천해주는 시스템입니다. 웹 크롤링 및 데이터 전처리를 통해 수집된 레시피 데이터를 활용하여, 개인화된 추천을 제공합니다. 사용자 친화적인 인터페이스를 통해 새로운 요리를 쉽게 발견할 수 있는 기회를 제공합니다.

## 특징
- **개인화된 추천**: 사용자가 입력한 재료에 따라 적합한 레시피를 추천합니다.
- **대체재료 추천**: 사용자가 입력한 레시피의 주재료를 대체할 수 있는 적합한 재료를 추천합니다.
- **웹 크롤링**: 다양한 요리 데이터를 수집하기 위해 웹 크롤링 기술을 사용합니다.
- **효율성**: KMeans 클러스터링 및 LSH 알고리즘을 활용하여 유사한 레시피를 신속하게 찾아냅니다.

## 데이터 수집 과정
1. **웹 크롤링 및 스크래핑**: Selenium과 BeautifulSoup을 사용하여 레시피 데이터를 수집합니다.
2. **전처리**: 결측값 및 중복 데이터를 정리하고, 데이터 형식을 통일합니다. 
3. **데이터 저장**: 최종 데이터를 CSV 형식으로 저장하여 손쉽게 사용할 수 있도록 합니다.

## 사용 기술
- **Python**: 애플리케이션 구축에 사용되었습니다.
- **주요 라이브러리**:
  - `requests`: HTTP 요청 처리
  - `BeautifulSoup`: 웹 크롤링 및 스크래핑
  - `pandas`: 데이터 분석 및 조작
  - `datasketch`: LSH 및 Minhash 지원
  - `re`: 정규 표현식 처리

## 알고리즘
- 이 시스템은 두 가지 방법을 사용하여 구현됩니다.
  - **Locality Sensitive Hashing (LSH)**: Cosine similarity를 사용하여 가장 많은 재료가 겹치는 레시피를 추천합니다.
  - **MinHashing**: MinHashing을 활용하여 효율적으로 LSH를 계산하도록 도와줍니다.
  - **K-Means**: Clustering을 활용하여 대체재료를 추천합니다.

## 데이터 구조
- **항목**: 레시피 이름, 재료, 만드는 순서, 인분, 조리 시간, 음식 카테고리
- 카테고리와 조리법을 통해 더 정확한 추천이 가능하도록 설계되었습니다.

## 설치 및 실행
1. 필요한 라이브러리를 설치합니다.
   ```bash
   pip install requests beautifulsoup4 pandas datasketch
2. 데이터를 크롤링 및 스크래핑 합니다.
   ```bash
   python3 data_min/10000_recipes/mining.py
   python3 data_min/all_recipe/save_scraping_allrecipes_category.py
3. 레시피를 추천 받습니다.(threshold를 변경하세요)
   ```bash
   python3 recommendation_algorithm/offering_recipes_allrecipes.py
   python3 recommendation_algorithm/offering_recipes_10000recipes.py
5. 대체재료를 찾습니다
   ```bash
   python3 k-means_algorithm/knn.py
