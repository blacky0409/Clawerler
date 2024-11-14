from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import json
from googletrans import Translator  # 번역 라이브러리 추가

# Chrome WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 번역기 초기화
translator = Translator()

# 카테고리 페이지로 이동
driver.get("https://www.allrecipes.com/recipes-a-z-6735880")
time.sleep(3)

# BeautifulSoup으로 현재 페이지 HTML 분석
soup = BeautifulSoup(driver.page_source, "html.parser")

# 각 카테고리 링크 추출
meal_links = soup.find_all("a", class_="mntl-link-list__link")
meal_urls = [link.get('href') for link in meal_links]

# 링크가 없다면 종료
if not meal_urls:
    print("No meal links found.")
    driver.quit()
    exit()

# 크롤링한 데이터 저장할 리스트
recipe_data = []

# 각 카테고리 링크에 대해 처리
for meal_url in meal_urls:
    driver.get(meal_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    recipe_links = soup.find_all("a", class_="mntl-card-list-items")

    for recipe_link in recipe_links:
        recipe_url = recipe_link.get("href")
        driver.get(recipe_url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 요리 제목 추출 및 번역
        title_element = soup.find("h1", class_="article-heading text-headline-400")
        title = title_element.get_text(strip=True) if title_element else "제목 없음"
        title_ko = translator.translate(title, src='en', dest='ko').text  # 번역 추가

        # 총 시간 추출
        total_time_element = soup.find("div", class_="mm-recipes-details__value")
        total_time = total_time_element.get_text(strip=True) if total_time_element else None
        if not total_time:
            continue

        # 인분 수 추출 및 번역
        servings_element = soup.find("div", class_="mm-recipes-details__value")
        servings = servings_element.get_text(strip=True) if servings_element else "제공 인원수 없음"
        servings_ko = translator.translate(servings, src='en', dest='ko').text  # 번역 추가

        # 재료 추출 및 번역
        ingredients_list = soup.find("ul", class_="mm-recipes-structured-ingredients__list")
        ingredients_ko = []
        if ingredients_list:
            for item in ingredients_list.find_all("li", class_="mm-recipes-structured-ingredients__list-item"):
                ingredient_text = " ".join(span.get_text(strip=True) for span in item.find_all("span"))
                ingredients_ko.append(translator.translate(ingredient_text, src='en', dest='ko').text)  # 번역 추가

        # 조리 과정 추출 및 번역
        directions_list = soup.find("ol", class_="mntl-sc-block-group--OL")
        directions_ko = []
        if directions_list:
            for step in directions_list.find_all("li", class_="mntl-sc-block-group--LI"):
                step_text = step.get_text(strip=True)
                directions_ko.append(translator.translate(step_text, src='en', dest='ko').text)  # 번역 추가

        # 레시피 데이터를 딕셔너리 형태로 저장
        recipe = {
            "Title": title_ko,
            "Total Time": total_time,
            "Servings": servings_ko,
            "Ingredients": ingredients_ko,
            "Directions": directions_ko
        }
        recipe_data.append(recipe)

# CSV 파일로 저장하는 함수
def save_to_csv(data, filename="recipes.csv"):
    headers = ["Title", "Total Time", "Servings", "Ingredients", "Directions"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for recipe in data:
            writer.writerow([
                recipe["Title"],
                recipe["Total Time"],
                recipe["Servings"],
                "; ".join(recipe["Ingredients"]),
                "\n".join(recipe["Directions"])
            ])

# JSON 파일로 저장하는 함수
def save_to_json(data, filename="recipes.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 크롤링한 데이터를 CSV와 JSON 파일로 저장
save_to_csv(recipe_data, filename="recipes.csv")
save_to_json(recipe_data, filename="recipes.json")

# 브라우저 종료
driver.quit()
