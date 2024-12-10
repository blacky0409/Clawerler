from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from googletrans import Translator
import csv

# Chrome WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
translator = Translator()

# 대상 페이지로 이동
driver.get("https://www.allrecipes.com/ingredients-a-z-6740416")
time.sleep(3)

# BeautifulSoup으로 현재 페이지 HTML 분석
soup = BeautifulSoup(driver.page_source, "html.parser")

# 각 재료 페이지 링크 추출
ingredient_links = soup.find_all("a", class_="mntl-link-list__link")
ingredient_urls = [link.get("href") for link in ingredient_links]

# 크롤링한 데이터 저장할 리스트
recipe_data = []

# 각 재료 페이지에 접근하여 레시피 크롤링
for ingredient_url in ingredient_urls:
    try:
        driver.get(ingredient_url)
        time.sleep(3)

        # 카테고리 제목 추출
        soup = BeautifulSoup(driver.page_source, "html.parser")
        category_title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "카테고리 제목 없음"
        print(f"[INFO] 현재 카테고리: {category_title}")  # 실시간 카테고리 출력

        # 각 레시피 링크 추출
        recipe_links = soup.find_all("a", class_="mntl-card-list-items")
        recipe_urls = [link.get("href") for link in recipe_links]

        # 각 레시피 페이지에서 정보 추출
        for recipe_url in recipe_urls:
            try:
                driver.get(recipe_url)
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # 제목 추출 및 번역
                title_element = soup.find("h1", class_="article-heading text-headline-400")
                title = title_element.get_text(strip=True) if title_element else "제목 없음"
                try:
                    title_ko = translator.translate(title, src='en', dest='ko').text
                except Exception:
                    title_ko = title  # 번역 실패 시 원래 텍스트 사용
                print(f" - 레시피 제목: {title_ko}")  # 실시간 제목 출력

                # 총 시간 추출 (없으면 저장하지 않음)
                total_time_element = soup.find("div", class_="mm-recipes-details__value")
                total_time = total_time_element.get_text(strip=True) if total_time_element else None
                if not total_time:
                    print("   -> 총 시간이 없어 건너뜀")
                    continue

                # 인분 수 추출
                servings = "제공 인원수 없음"
                servings_item = soup.find_all("div", class_="mm-recipes-details__item")
                for item in servings_item:
                    label = item.find("div", class_="mm-recipes-details__label")
                    value = item.find("div", class_="mm-recipes-details__value")
                    if label and value and label.get_text(strip=True) == "Servings:":
                        servings = value.get_text(strip=True)
                        break
                
                # 인분 번역
                try:
                    servings_ko = translator.translate(servings, src='en', dest='ko').text
                except Exception:
                    servings_ko = servings  # 번역 실패 시 원래 텍스트 사용
                print(f"   -> 제공 인원수: {servings_ko}")  # 실시간 인분 출력

                # 재료 추출 및 번역
                ingredients_list = soup.find("ul", class_="mm-recipes-structured-ingredients__list")
                ingredients_ko = []
                if ingredients_list:
                    for item in ingredients_list.find_all("li", class_="mm-recipes-structured-ingredients__list-item"):
                        ingredient_text = " ".join(span.get_text(strip=True) for span in item.find_all("span"))
                        try:
                            translated_text = translator.translate(ingredient_text, src='en', dest='ko').text
                        except Exception:
                            translated_text = ingredient_text  # 번역 실패 시 원래 텍스트 사용
                        ingredients_ko.append(translated_text)
                print(f"   -> 재료 개수: {len(ingredients_ko)}개")  # 실시간 재료 개수 출력

                # 조리 과정 추출 및 번역 (숫자 순서 포함)
                directions_list = soup.find("ol", class_="mntl-sc-block-group--OL")
                directions_ko = []
                if directions_list:
                    for idx, step in enumerate(directions_list.find_all("li", class_="mntl-sc-block-group--LI"), start=1):
                        step_text = step.get_text(strip=True)
                        try:
                            translated_text = translator.translate(step_text, src='en', dest='ko').text
                        except Exception:
                            translated_text = step_text  # 번역 실패 시 원래 텍스트 사용
                        directions_ko.append(f"{idx}. {translated_text}")
                print(f"   -> 조리 단계: {len(directions_ko)}단계")  # 실시간 조리 단계 출력

                # 레시피 데이터 저장
                recipe_data.append([
                    category_title, title_ko, total_time, servings_ko,
                    ", ".join(ingredients_ko), " ".join(directions_ko)
                ])
                print("   -> 레시피 저장 완료!\n")
            except Exception as e:
                print(f"Error processing recipe {recipe_url}: {e}")
                continue
    except Exception as e:
        print(f"Error processing ingredient page {ingredient_url}: {e}")
        continue

# CSV 파일로 저장
output_file = "recipes_data.csv"
with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Category", "Title (Korean)", "Total Time", "Servings (Korean)", "Ingredients (Korean)", "Directions (Korean)"])
    writer.writerows(recipe_data)

print(f"[INFO] 데이터가 '{output_file}'에 저장되었습니다!")

# 브라우저 종료
driver.quit()
