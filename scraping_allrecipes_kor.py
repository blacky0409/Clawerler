from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from googletrans import Translator  # 번역 라이브러리 추가
import time

# Chrome WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 번역기 초기화
translator = Translator()

# 카테고리 페이지로 이동
driver.get("https://www.allrecipes.com/recipes-a-z-6735880")
time.sleep(3)  # 페이지 로딩 대기

# BeautifulSoup으로 현재 페이지 HTML 분석
soup = BeautifulSoup(driver.page_source, "html.parser")

# 각 카테고리 링크 추출
meal_links = soup.find_all("a", class_="mntl-link-list__link")
meal_urls = [link.get('href') for link in meal_links]

# 링크가 없다면 종료
if not meal_urls:
    print("No meal links found.")
    driver.quit()
    exit()  # 프로그램 종료

# 각 카테고리 링크에 대해 처리
for meal_url in meal_urls:
    driver.get(meal_url)
    time.sleep(3)  # 페이지 로딩 대기

    # 레시피 링크 추출
    soup = BeautifulSoup(driver.page_source, "html.parser")
    recipe_links = soup.find_all("a", class_="mntl-card-list-items")

    for recipe_link in recipe_links:
        recipe_url = recipe_link.get("href")
        driver.get(recipe_url)
        time.sleep(3)  # 페이지 로딩 대기

        # 레시피 데이터 추출
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 요리 제목 추출 및 번역
        title_element = soup.find("h1", class_="article-heading text-headline-400")
        title = title_element.get_text(strip=True) if title_element else "제목 없음"
        title_ko = translator.translate(title, src='en', dest='ko').text

        # 총 시간 추출 (없으면 해당 레시피 건너뜀)
        total_time_element = soup.find("div", class_="mm-recipes-details__value")
        if not total_time_element:
            continue  # 총 시간이 없으면 다음 레시피로 이동
        total_time = total_time_element.get_text(strip=True)
        total_time_ko = translator.translate(total_time, src='en', dest='ko').text

        # 인분 수 추출 및 번역
        servings_element = soup.find("div", class_="mm-recipes-details__value")
        servings = servings_element.get_text(strip=True) if servings_element else "인원 정보 없음"
        servings_ko = translator.translate(servings, src='en', dest='ko').text

        # 재료 추출 및 번역
        ingredients_list = soup.find("ul", class_="mm-recipes-structured-ingredients__list")
        ingredients_ko = []
        if ingredients_list:
            for item in ingredients_list.find_all("li", class_="mm-recipes-structured-ingredients__list-item"):
                ingredient_text = " ".join(span.get_text(strip=True) for span in item.find_all("span"))
                ingredients_ko.append(translator.translate(ingredient_text, src='en', dest='ko').text)

        # 조리 과정 추출 및 번역
        directions_list = soup.find("ol", class_="mntl-sc-block-group--OL")
        directions_ko = []
        if directions_list:
            for step in directions_list.find_all("li", class_="mntl-sc-block-group--LI"):
                step_text = step.get_text(strip=True)
                directions_ko.append(translator.translate(step_text, src='en', dest='ko').text)

        # 번역된 데이터를 출력
        print(f"제목: {title_ko}")
        print(f"총 시간: {total_time_ko}")
        print(f"인분: {servings_ko}")
        print("재료:")
        for ingredient in ingredients_ko:
            print(f"- {ingredient}")
        print("조리 과정:")
        for i, step in enumerate(directions_ko, 1):
            print(f"{i}. {step}")
        print("\n" + "="*50 + "\n")

# 브라우저 종료
driver.quit()
